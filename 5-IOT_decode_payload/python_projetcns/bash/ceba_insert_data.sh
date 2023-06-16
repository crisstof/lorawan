#!/bin/bash

set -e
set -u

#Verification du dossier passé en argument
[ $# == 5 ] || >&2 echo "Erreur: 5 arguments sont nécessaires. Chemin absolu vers les fichiers JSON | Nom du schema de stockage | Nom du serveur de base de données | Nom utilisateur en base de données | L'AppName de stockage des données capteurs." | exit
[ -d "$1" ] || >&2 echo "Erreur: $1 n'est pas un dossier." | exit

#Check si le chemin du dossier est complet
[[ $1 = /* ]] || >&2 echo "Erreur: Le chemin vers le dossier ciblé doit être absolu." | exit

directory=$1

#Verification de l'installation de jq
command -v jq >/dev/null 2>&1 || { echo >&2 "Erreur: JQ est necessaire pour faire fonctionner ce script."; exit 1; }

[[ $3 = "cebasms01" || $3 = "cebabdd01" ]] || >&2 echo "Erreur: $3 n'est pas un serveur valide." | exit

[[ $4 = "cebatest" || $4 = "cebauser" ]] || >&2 echo "Erreur: $4 n'est pas un utilisateur valide." | exit

#Check aussi les combos serveur/user

#Verification du nom du schéma passé en paramètre
schema=$2
check_schema=`psql -q -h $3 -X -U $4 -d datastorage -t -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '$schema'"`

#Si le schéma n'existe pas
if [[ $check_schema == "" ]]
then
	
	>&2 echo "Erreur: Le schéma $schema n'existe pas."
	exit
	
fi

#Suppression du fichier temporaire s'il est toujours présent
rm -f /tmp/requetesCEBA.sql

#Recuperation de la liste des fichiers dans le dossier
filesList=$(echo "$(ls ${directory}/*.json | xargs -n 1 basename)")

#Recuperation du nombre de fichiers dans le dossier
files=$(echo "$filesList" | wc -w)

#Si l'appName n'existe pas, on essaye de créer la table correspondante "json_appname_row" ainsi que la table "json_file"
#Verification si la table json_file existe dans le schema passé en parametre
psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $schema.json_file(id serial UNIQUE,file_name TEXT,app_name TEXT,upload_state BOOLEAN,date_insert TIMESTAMP,PRIMARY KEY(file_name,app_name))"

#Recuperation de la liste des application Name dans la table correspondante
appNameList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT DISTINCT LOWER(app_name) FROM $schema.json_file"`
appName=$(echo "$5")
appName=${appName//\"} #On enleve les guillemets
appName=$(echo "$appName" | tr - _) #On remplace les - par des _
appNameLower=$(echo "$appName" | tr '[:upper:]' '[:lower:]')

tableName="Json_"$appName"_row"

if ! [[ $appNameList =~ (^|[[:space:]])$appNameLower($|[[:space:]]) ]];
then
	echo "CREATION D'UNE TABLE POUR $appName"
	psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TABLE IF NOT EXISTS $schema.$tableName (line_number INTEGER, data jsonb NOT NULL, file_id INTEGER, geo_point geometry, PRIMARY KEY(line_number, file_id),CONSTRAINT json_file_id_fk FOREIGN KEY(file_id) REFERENCES $schema.json_file(id) MATCH FULL)"
					
	#Liaison de la table avec le trigger
	psql -q -h $3 -X -U $4 -d datastorage -t -c "CREATE TRIGGER onInsert$appName BEFORE INSERT ON $schema.$tableName FOR EACH ROW EXECUTE PROCEDURE onInsertAddGeo()"
					
	#Mise a jour de la liste des appName
	appNameList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT DISTINCT app_name FROM $schema.json_file"`
fi

#Si le nombre est superieur à 0
if [ $files -gt 0 ]
then
	
		#Pour chaque fichier dans le dossier
		for nomFichier in $filesList
		do	
			
			if [ $schema == "connecsens" ]
			then
			
				#S'il s'agit du fichier du jour, on skip pour ne pas perdre de données
				dateAjd=$(echo "$(date +%Y%m%d)")
				dateFichier=$(echo $nomFichier | cut -b 5-12)	
				
				if [ $dateAjd == $dateFichier ]
				then
					#On ne lit pas ce fichier
					continue
				fi

				#Lecture du fichier connecsens car il ne date pas d'aujourd'hui
				
			fi
			
			#Recupération de la liste des fichiers déjà en base
			DbFilesList=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT file_name from $schema.json_file where app_name='$appName' and upload_state = true"`

			#Verification si le fichier en lecture est déjà en base
			if ! [[ $DbFilesList == *"$nomFichier"* ]];
			then
			
				#Debut
				timestamp=$(date +"%T")
				echo "$timestamp: DEBUT DU TRAITEMENT DU FICHIER $nomFichier"

				#Insertion du nom du fichier JSON dans la table correspondante
				psql -q -h $3 -X -U $4 -d datastorage -t -c "INSERT INTO $schema.json_file(file_name,app_name,upload_state) VALUES('$nomFichier','$appName','false')"

				#Recuperation de l'ID du nom du fichier JSON
				id=`psql -h $3 -X -U $4 -d datastorage -t -c "SELECT id FROM $schema.json_file WHERE file_name='$nomFichier' AND app_name='$appName'"`

				#Boucle de lecture du fichier JSON
				declare -i cpt=0
				while read -r line; do
				
					cpt=$((cpt+1))
				
					#Insertion dans la table json correspondante
					echo "INSERT INTO $schema.$tableName (line_number, data, file_id) VALUES($cpt, '$line', $id);" >> /tmp/requetesCEBA.sql

				done < "${1}/$nomFichier" #Fin de la boucle du fichier
	
				psql -q -h $3 -X -U $4 -d datastorage -f /tmp/requetesCEBA.sql
			
				#Mise à jour de l'état de l'upload du fichier JSON
				psql -q -h $3 -X -U $4 -d datastorage -t -c "UPDATE $schema.json_file SET upload_state = 'true' , date_insert = current_timestamp WHERE id = '$id'"		

				timestamp=$(date "+%T")
				echo "$timestamp: TRAITEMENT DU FICHIER $nomFichier TERMINÉ"
				echo "Lignes insérées: $cpt"
			
				#Suppression du fichier temporaire
				rm -f /tmp/requetesCEBA.sql
	
			fi
		done		
fi
