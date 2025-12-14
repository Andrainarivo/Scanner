pipeline {
    agent any
    
    environment {
        // Jenkins credentials ID
        DOCKER_CRED_ID = 'docker-hub-creds'
        DOCKER_REGISTRY = 'docker.io'
        // Base image name (no unnecessary suffix)
        DOCKER_IMAGE_NAME = "doda0101/nmap-app"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build & Push to Docker Hub') {
            steps {
                script {
                    // Create unique tag based on the Git commit
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    // Name the image: doda0101/nmap-app:a1b2c3d
                    def fullImageName = "${env.DOCKER_IMAGE_NAME}:${gitCommit}"

                    echo "Building image: ${fullImageName}"

                    // 1. Authentification Docker Hub
                    withCredentials([usernamePassword(credentialsId: env.DOCKER_CRED_ID, 
                                                    passwordVariable: 'DOCKER_PASSWORD', 
                                                    usernameVariable: 'DOCKER_USERNAME')]) {
                        sh "docker login -u ${DOCKER_USERNAME} -p ${DOCKER_PASSWORD} ${DOCKER_REGISTRY}"
                    }

                    // 2. Build
                    sh "docker build -t ${fullImageName} ."

                    // 3. Push
                    sh "docker push ${fullImageName}"

                    // 4. Sauvegarde du nom pour l'étape suivante
                    env.DEPLOY_IMAGE = fullImageName
                }
            }
        }
        
        stage('Deploy to K8s') {
            steps {
                script {
                    echo "Updating Minikube with: ${env.DEPLOY_IMAGE}"

                    // The regex looks for 'image: doda0101/nmap-app:...' and replaces the tag
                    // This will update api.yml AND worker.yml with the same new image
                    sh "sed -i 's|image: ${env.DOCKER_IMAGE_NAME}:.*|image: ${env.DEPLOY_IMAGE}|g' k8s/api.yml"
                    sh "sed -i 's|image: ${env.DOCKER_IMAGE_NAME}:.*|image: ${env.DEPLOY_IMAGE}|g' k8s/worker.yml"

                    // Application des changements
                    sh "kubectl apply -f k8s/api.yml"
                    sh "kubectl apply -f k8s/worker.yml"

                    // Wait for the rollout to complete
                    // 60s timeout to avoid hanging the pipeline indefinitely if something fails
                    timeout(time: 60, unit: 'SECONDS') {
                        sh "kubectl rollout status deployment/nmap-api"
                        sh "kubectl rollout status deployment/nmap-worker"
                    }
                }
            }
        }
    }

    // Cleanup step (runs always, on success or failure)
    post {
        always {
            script {
                // Remove the local image to free space on the Jenkins server
                // Check the variable exists first to avoid an error
                if (env.DEPLOY_IMAGE) {
                    sh "docker rmi ${env.DEPLOY_IMAGE} || true"
                    sh "docker logout || true"
                }
            }
        }
    }
}