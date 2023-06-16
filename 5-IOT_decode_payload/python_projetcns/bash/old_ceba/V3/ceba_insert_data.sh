#!/bin/bash

set -e
set -u

#Verification du dossier passé en argument
[ $# == 4 ] || >&2 echo "Erreur: 4 arguments sont nécessaires. Chemin absolu vers les fichiers JSON | Nom du schema de stockage | Nom du serveur de base de données | Nom utilisateur en base de données." | exit
[ -d "$1" ] || >&2 echo "Erreur: $1 n'est pas un dossier." | exit

#Check si le chemin du dossier est complet
[[ $1 = /* ]] || >&2 echo "Erreur: Le chemin vers le dossier ciblé doit être absolu." | exit

directory=$1

#Verification de l'installation de jq
command -v jq >/dev/null 2>&1 || { echo >&2 "Erreur: JQ est necessaire pour faire fonctionner ce script."; exit 1; }

[[ $3 = "cebasms01" || $3 = "cebabdd01" ]] || >&2 echo "Erreur: $3 n'est pas un serveur valide." | exit

[[ $4 = "cebatest" || $4 = "cebauser" ]] || >&2 echo "Erreur: $4 n'est pas un serveur valide." | exit

#Check aussi les combos serveur/user

#Verification du nom du schéma passé en paramètre
project=$2
project_schema=`psql -q -h $3 -X -U $4 -d datastorage -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '$project'"`

#Si le schéma n'existe pas
if [[ $project_schema == "" ]]
then
	
	>&2 echo "Erreur: Le schéma $project n'existe pas."
	exit
	
fi

#Suppression du fichier temporaire s'il est toujours présent
rm -f /tmp/requetesCEBA.sql

#Recuperation de la liste des fichiers dans le dossier
filesList=$(echo "$(ls ${directory}/*.json | xargs -n 1 basename)")

#Recuperation du nombre de fichiers dans le dossier
files=$(echo "$filesList" | wc -w)

#Si le nombre est superieur à 0
if [ $files -gt 0 ]
then
	
	#Le traitement est différent suivant la typologie du réseau de capteurs
	if [ $project == "connecsens" ]
	then

		#Verification si la table json_file existe dans le schema passé en parametre
		psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_file(id serial UNIQUE,file_name TEXT,app_name TEXT,upload_state BOOLEAN,PRIMARY KEY(file_name,app_name))"

		#Recuperation de la liste des application Name dans la table correspondante
		appNameList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT DISTINCT app_name FROM $project.json_file"`
	
		#Pour chaque fichier dans le dossier
		for nomFichier in $filesList
		do	
			#S'il s'agit du fichier du jour, on skip pour ne pas perdre de données
			
			dateAjd=$(echo "$(date +%Y%m%d)")
			dateFichier=$(echo $nomFichier | cut -b 5-12)	
			
			if [ $dateAjd == $dateFichier ]
			then
				#On ne lit pas ce fichier
				continue
			fi

			#Lecture du fichier car il ne date pas d'aujourd'hui

			#Recuperation de l'appName du fichier en cours
			firstLine=$(head -n 1 ${1}/$nomFichier)
		
			#Recuperation de lAppName de la premiere ligne JSON, représentant l'appName du fichier
			#RAPPEL:Un fichier connecSens est relié à un seul applicationName
			appName=$(echo "$firstLine" | jq '.applicationName')
			appName=${appName//\"} #On enleve les guillemets
			appName=$(echo "$appName" | tr - _) #On remplace les - par des _

			#Recupération de la liste des fichiers déjà en base
			DbFilesList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT file_name from $project.json_file where app_name='$appName' and upload_state = true"`

			#Verification si le fichier en lecture est déjà en base
			if ! [[ $DbFilesList == *"$nomFichier"* ]];
			then
			
				#Debut
				timestamp=$(date +"%T")
				echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

				#Insertion du nom du fichier JSON dans la table correspondante
				psql -q -h $3 -X -U $4 -d datastorage -t -c "INSERT INTO $project.json_file(file_name,app_name,upload_state) VALUES('$nomFichier','$appName','false')"

				#Recuperation de l'ID du nom du fichier JSON
				id=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT id FROM $project.json_file WHERE file_name='$nomFichier' AND app_name='$appName'"`

				#Verification de l'existance de l'appName dans la table
				#Si oui, insertion des lignes Json dans la table correspondante
				#sinon création de la nouvelle table json + ajout de l'appName dans la table des appname + insertion dans la nouvelle table json
				tableName="Json_"$appName"_row"

				if ! [[ $appNameList =~ (^|[[:space:]])$appName($|[[:space:]]) ]];
				then
					echo "CREATION D'UNE TABLE POUR $appName"
					psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.$tableName (line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, geo_point geometry, PRIMARY KEY(line_number, file_id),CONSTRAINT json_file_id_fk FOREIGN KEY(file_id) REFERENCES $project.json_file(id) MATCH FULL)"
					
					#Liaison de la table avec le trigger
					psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TRIGGER onInsert$appName BEFORE INSERT ON $project.$tableName FOR EACH ROW EXECUTE PROCEDURE onInsertAddGeo()"
					
					#Mise a jour de la liste des appName
					appNameList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT DISTINCT app_name FROM $project.json_file"`
				fi


				#Boucle de lecture du fichier JSON
				declare -i cpt=0
				while read -r line; do
				
					cpt=$((cpt+1))
				
					#Insertion dans la table json correspondante
					echo "INSERT INTO $project.$tableName (line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /tmp/requetesCEBA.sql

				done < "${1}/$nomFichier" #Fin de la boucle du fichier
	
				psql -q -h $3 -X -U $4 -d datastorage -f /tmp/requetesCEBA.sql
			
				#Mise à jour de l'état de l'upload du fichier JSON
				psql -q -h $3 -X -U $4 -d datastorage -t -c "UPDATE $project.json_file SET upload_state = 'true' WHERE id = '$id'"		

				timestamp=$(date "+%T")
				echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
				echo "Lignes insérées: $cpt"
			
				#Suppression du fichier temporaire
				rm -f /tmp/requetesCEBA.sql
	
			fi
		done	
	elif [ $project == "tmp_covid" ]
	then
		#Il s'agit du projet Covid
			
		psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_file(id serial UNIQUE,file_name TEXT,upload_state BOOLEAN,PRIMARY KEY(file_name))"
		psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_row(line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, PRIMARY KEY(line_number, file_id), FOREIGN KEY(file_id) REFERENCES $project.json_file(id) MATCH FULL)"
						
		#Suppression des données déjà en base
		#Le fichier de données du Covid contient toutes les données jusqu'à présent

		psql -q -h $3 -X -U $4 -d datastorage -t -c "Delete from $project.json_row"
		psql -q -h $3 -X -U $4 -d datastorage -t -c "Delete from $project.json_file"

		#Pour chaque fichier dans le dossier
		for nomFichier in $filesList
		do	
        		
			#Recupération de la liste des fichiers déjà en base
			DbFilesList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT file_name from $project.json_file"`

			#Verification si le fichier en lecture est déjà en base
			if ! [[ $DbFilesList == *"$nomFichier"* ]];
			then

				#Debut
				timestamp=$(date +"%T")
				echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

				#Insertion du nom du fichier JSON dans la table correspondante
				psql -q -h $3 -X -U $4 -d datastorage -t -c "INSERT INTO $project.json_file(file_name,upload_state) VALUES('$nomFichier','false')"

				#Recuperation de l'ID du nom du fichier JSON
				id=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT id FROM $project.json_file WHERE file_name='$nomFichier'"`

				#Boucle de lecture du fichier JSON
				declare -i cpt=0
				while read -r line; do

						cpt=$((cpt+1))

						#Insertion dans la table json correspondante
						echo "INSERT INTO $project.json_row(line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /tmp/requetesCEBA.sql

				done < "${1}/$nomFichier" #Fin de la boucle du fichier

				psql -q -h $3 -X -U $4 -d datastorage -f /tmp/requetesCEBA.sql

				#Mise à jour de l'état de l'upload du fichier JSON
				psql -q -h $3 -X -U $4 -d datastorage -t -c "UPDATE $project.json_file SET upload_state = 'true' WHERE id = '$id'"

				timestamp=$(date "+%T")
				echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
				echo "Lignes insérées: $cpt"

				#Suppression du fichier temporaire
				rm -f /tmp/requetesCEBA.sql

			fi
		done
		
	else #Il s'agit donc d'un projet autre que connecsens
		
		psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_file(id serial UNIQUE,file_name TEXT,upload_state BOOLEAN,PRIMARY KEY(file_name))"
		psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_row(line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, geo_point geometry, PRIMARY KEY(line_number, file_id), FOREIGN KEY(file_id) REFERENCES $project.json_file(id) MATCH FULL)"
		
		#Pour chaque fichier dans le dossier
		for nomFichier in $filesList
		do	
					
			#Recupération de la liste des fichiers déjà en base
			DbFilesList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT file_name from $project.json_file"`

			#Verification si le fichier en lecture est déjà en base
			if ! [[ $DbFilesList == *"$nomFichier"* ]];
			then

				#Debut
				timestamp=$(date +"%T")
				echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

				#Insertion du nom du fichier JSON dans la table correspondante
				psql -q -h $3 -X -U $4 -d datastorage -t -c "INSERT INTO $project.json_file(file_name,upload_state) VALUES('$nomFichier','false')"

				#Recuperation de l'ID du nom du fichier JSON
				id=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT id FROM $project.json_file WHERE file_name='$nomFichier'"`

				#Boucle de lecture du fichier JSON
				declare -i cpt=0
				while read -r line; do

						cpt=$((cpt+1))

						#Insertion dans la table json correspondante
						echo "INSERT INTO $project.json_row(line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /tmp/requetesCEBA.sql

				done < "${1}/$nomFichier" #Fin de la boucle du fichier

				psql -q -h $3 -X -U $4 -d datastorage -f /tmp/requetesCEBA.sql

				#Mise à jour de l'état de l'upload du fichier JSON
				psql -q -h $3 -X -U $4 -d datastorage -t -c "UPDATE $project.json_file SET upload_state = 'true' WHERE id = '$id'"

				timestamp=$(date "+%T")
				echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
				echo "Lignes insérées: $cpt"

				#Suppression du fichier temporaire
				rm -f /tmp/requetesCEBA.sql

			fi
		done
	fi
	
fi
