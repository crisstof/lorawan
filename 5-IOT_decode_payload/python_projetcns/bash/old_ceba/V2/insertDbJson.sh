#!/bin/bash

set -e
set -u

#Verification du dossier passé en argument
[ $# == 2 ] || >&2 echo "Erreur: Deux arguments sont nécessaires." | exit
[ -d "$1" ] || >&2 echo "Erreur: $1 n'est pas un dossier." | exit

#Check si le chemin du dossier est complet
[[ $1 = /* ]] || >&2 echo "Erreur: Le chemin vers le dossier ciblé doit être absolu." | exit

directory=$1

#Verification de l'installation de jq
command -v jq >/dev/null 2>&1 || { echo >&2 "Erreur: JQ est necessaire pour faire fonctionner ce script."; exit 1; }

#Verification du nom du schéma passé en paramètre
project=$2
project_schema=`psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '$project'"`

#Si le schéma n'existe pas
if [[ $project_schema == "" ]]
then
	
	>&2 echo "Erreur: Le schéma $project n'existe pas."
	exit
	
fi

#Suppression du fichier temporaire s'il est toujours présent
rm -f /home/loraserver/requetes.sql

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
		psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_file(id serial UNIQUE,file_name TEXT,app_name TEXT,upload_state BOOLEAN,PRIMARY KEY(file_name,app_name))"

		#Recuperation de la liste des application Name dans la table correspondante
		appNameList=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT DISTINCT app_name FROM $project.json_file"`
	

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
        		DbFilesList=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT file_name from $project.json_file where app_name='$appName' and upload_state = true"`

			#Verification si le fichier en lecture est déjà en base
			if ! [[ $DbFilesList == *"$nomFichier"* ]];
			then
		
				#Debut
				timestamp=$(date +"%T")
				echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

				#Insertion du nom du fichier JSON dans la table correspondante
				psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "INSERT INTO $project.json_file(file_name,app_name,upload_state) VALUES('$nomFichier','$appName','false')"

                        	#Recuperation de l'ID du nom du fichier JSON
                        	id=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT id FROM $project.json_file WHERE file_name='$nomFichier' AND app_name='$appName'"`

				#Verification de l'existance de l'appName dans la table
                        	#Si oui, insertion des lignes Json dans la table correspondante
                        	#sinon création de la nouvelle table json + ajout de l'appName dans la table des appname + insertion dans la nouvelle table json
				tableName="Json_"$appName"_row"

                        	if ! [[ $appNameList =~ (^|[[:space:]])$appName($|[[:space:]]) ]];
                        	then
        	        	        echo "CREATION D'UNE TABLE POUR $appName"

                	       		psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "CREATE TABLE $project.$tableName (line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, PRIMARY KEY(line_number, file_id))"
                        		psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "ALTER TABLE $project.$tableName ADD CONSTRAINT json_file_id_fk FOREIGN KEY(file_id) REFERENCES $project.json_file(id) MATCH FULL"
					#Mise a jour de la liste des appName
                                	appNameList=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT DISTINCT app_name FROM $project.json_file"`

                        	fi


				#Boucle de lecture du fichier JSON
				declare -i cpt=0
				while read -r line; do
				
					cpt=$((cpt+1))
				
					#Insertion dans la table json correspondante
					echo "INSERT INTO $project.$tableName (line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /home/loraserver/requetes.sql

				done < "${1}/$nomFichier" #Fin de la boucle du fichier
	
				psql -q -h cebasms01 -X -U cebatest -d datastorage -f /home/loraserver/requetes.sql
			
				#Mise à jour de l'état de l'upload du fichier JSON
				psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "UPDATE $project.json_file SET upload_state = 'true' WHERE id = '$id'"		
	
				timestamp=$(date "+%T")
				echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
				echo "Lignes insérées: $cpt"
			
				#Suppression du fichier temporaire
				rm -f /home/loraserver/requetes.sql
	
			fi
			
		done	
	else #Il s'agit donc d'un projet autre que connecsens
		
		#Pour chaque fichier dans le dossier
        	for nomFichier in $filesList
        	do		
			psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_file(id serial UNIQUE,file_name TEXT,upload_state BOOLEAN,PRIMARY KEY(file_name))"
       	 		psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $project.json_row(line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, PRIMARY KEY(line_number, file_id), FOREIGN KEY(file_id) REFERENCES $project.json_file(id) MATCH FULL)"
        		
			#Recupération de la liste des fichiers déjà en base
                        DbFilesList=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT file_name from $project.json_file"`

                        #Verification si le fichier en lecture est déjà en base
                        if ! [[ $DbFilesList == *"$nomFichier"* ]];
                        then

                                #Debut
                                timestamp=$(date +"%T")
                                echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

                                #Insertion du nom du fichier JSON dans la table correspondante
                                psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "INSERT INTO $project.json_file(file_name,upload_state) VALUES('$nomFichier','false')"

                                #Recuperation de l'ID du nom du fichier JSON
                                id=`psql -h cebasms01 -X -U cebatest -d datastorage -t -c "SELECT id FROM $project.json_file WHERE file_name='$nomFichier'"`

                                #Boucle de lecture du fichier JSON
                                declare -i cpt=0
                                while read -r line; do

                                        cpt=$((cpt+1))

                                        #Insertion dans la table json correspondante
                                        echo "INSERT INTO $project.json_row(line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /home/loraserver/requetes.sql

                                done < "${1}/$nomFichier" #Fin de la boucle du fichier

                                psql -q -h cebasms01 -X -U cebatest -d datastorage -f /home/loraserver/requetes.sql

                                #Mise à jour de l'état de l'upload du fichier JSON
                                psql -q -h cebasms01 -X -U cebatest -d datastorage -t -c "UPDATE $project.json_file SET upload_state = 'true' WHERE id = '$id'"

                                timestamp=$(date "+%T")
                                echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
                                echo "Lignes insérées: $cpt"

                                #Suppression du fichier temporaire
                                rm -f /home/loraserver/requetes.sql

                        fi
		done
	fi
	
fi
