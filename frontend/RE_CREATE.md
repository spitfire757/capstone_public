## How to create SkySynth from scratch

1: Initial backend:
    Create an AWS EC2 instance. Once created intall apache2, mysql, and use
    sudo apt-get install php*-mysql to install all necessary PDO drivers.
    Create a custom cronjob to update the apache2 dev files to the github as
    sym linking is finicky. 

    '''
    #!/bin/bashrsync 
    -av --delete /var/www/html/ /home/ubuntu/Capstone/src/
    '''

    In crontab -e
    
    '''
    * * * * * /usr/local/bin/sync_html_to_repo.sh
    '''


2: Pull from github 
