pipeline {
    agent any

    environment {
        CONTAINER_NAME = "flask-container"
        STUB_VALUE = "200"
    }
    
    parameters {
        choice choices: ['Baseline', 'APIs', 'Full'], description: 'Type of scan that is going to perform inside the container.', name: 'SCAN_TYPE'
        string description: 'Target URL to scan. (Must start with "http://" or "https://")', name: 'TARGET'
        booleanParam defaultValue: true, description: 'If wanna generate report.', name: 'GENERATE_REPORT'
    }
    
    stages {
        stage('Stubs-Replacement') {
            steps {
                // 'STUB_VALUE' Environment Variable declared in Jenkins Configuration
                echo "STUB_VALUE = ${STUB_VALUE}"
                sh "sed -i 's/<STUB_VALUE>/$STUB_VALUE/g' config.py"
                sh 'cat config.py'
            }
        }

        stage('Build') {
            steps {
                // Building new image
                sh 'docker image build -t $CONTAINER_NAME:latest .'
                sh 'docker image tag $CONTAINER_NAME:latest $CONTAINER_NAME:$BUILD_NUMBER'
                echo 'Image built'
            }
        }

        stage('Deploy'){
            steps {
                script{
                    if(BUILD_NUMBER == "1") {
                        sh 'docker run --name $CONTAINER_NAME -d -p 5000:5000 $CONTAINER_NAME'
                    }
                    else {
                        sh 'docker stop $CONTAINER_NAME'
                        sh 'docker rm $CONTAINER_NAME'
                        sh 'docker run --name $CONTAINER_NAME -d -p 5000:5000 $CONTAINER_NAME'
                    }
                }
            }
        }
        
        stage('Pipeline Info') {
            steps {
                echo '=== Paramater Initialization ==='
                echo """
                The current parameters are:
                    Scan Type: ${params.SCAN_TYPE}
                    Target URL: ${params.TARGET}
                    Generate report: ${params.GENERATE_REPORT}
                """
            }
        }
      
        stage('Setting up OWASP ZAP docker container') {
            steps {
                echo 'Pulling up last OWASP ZAP container --> Start'
                sh 'docker pull owasp/zap2docker-stable:latest'
                echo 'Pulling up last OWASP ZAP container --> End'
                echo 'starting container --> Start'
                sh 'docker run -dt --name owaspzap owasp/zap2docker-stable /bin/bash '
            }
        }
      
        stage('Prepare work folder for report generation') {
            when {
                environment name: 'GENERATE_REPORT', value: 'true'
            }
            steps {
                sh 'docker exec owaspzap mkdir /zap/wrk'
            }
        }
      
        stage('Scanning target by owaspzap container') {
            steps {
                script {
                    scan_type = "${params.SCAN_TYPE}"
                    echo "---> scan_type: $scan_type"
                    target = "${params.TARGET}"
                    if(scan_type == 'Baseline'){
                        sh "docker exec owaspzap zap-baseline.py -t $target -r report.html -I"
                    }
                    else if(scan_type == "APIs"){
                        sh "docker exec owaspzap zap-api-scan.py -t $target -r report.html -I"
                    }
                    else if(scan_type == "Full"){
                        sh "docker exec owaspzap zap-full-scan.py -t $target -r report.html -I"
                    }
                    else{
                        echo 'Someting went wrong...'
                    }
                }
            }
        }
      
        stage('Copy report from zap container to external folder') {
            steps {
                script{
                    if (! fileExists("${env.JENKINS_HOME}/zapReport")){
                        sh "mkdir ${env.JENKINS_HOME}/zapReport"
                    }
                    sh "docker cp owaspzap:/zap/wrk/report.html ${env.JENKINS_HOME}/zapReport/report_${env.BUILD_ID}.html"
                }
            }
        }
    }
    
    post {
        always {
            echo 'Removing container'
            sh 'docker stop owaspzap'
            sh 'docker rm owaspzap'
            cleanWs()
            dir("${env.WORKSPACE}@tmp"){
                deleteDir()
            }
        }
    }
}