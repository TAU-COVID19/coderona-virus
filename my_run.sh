#!/bin/bash 
rm info.txt
sudo docker rm -f coderona_container
sudo docker rmi coderona_image
sudo docker build -t coderona_image .
sudo docker run --name coderona_container coderona_image &
sleep 3
sudo docker stats --format "table {{.Name}}\t{{.MemUsage}}" coderona_container > Bene_beraq_info_singleCpu_paper1.txt

