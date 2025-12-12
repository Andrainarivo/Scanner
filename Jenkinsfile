pipeline {
    agent any
    
    environment {
        // ID des credentials configurés dans Jenkins
        DOCKER_CRED_ID = 'docker-hub-credentials'
        DOCKER_REGISTRY = 'docker.io'
        // Nom de base de l'image (sans suffixe inutile pour simplifier)
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
                    // Création du tag unique basé sur le commit Git
                    def gitCommit = sh(returnStdout: true, script: 'git rev-parse --short HEAD').trim()
                    // On nomme l'image : doda0101/nmap-app:a1b2c3d
                    def fullImageName = "${env.DOCKER_IMAGE_NAME}:${gitCommit}"

                    echo "Construction de l'image : ${fullImageName}"

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
                    echo "Mise à jour de Minikube avec : ${env.DEPLOY_IMAGE}"
                    
                    // La regex cherche 'image: doda0101/nmap-app:...' et remplace tout le tag
                    // Cela mettra à jour api.yml ET worker.yml avec la même nouvelle image
                    sh "sed -i 's|image: ${env.DOCKER_IMAGE_NAME}:.*|image: ${env.DEPLOY_IMAGE}|g' k8s/api.yml"
                    sh "sed -i 's|image: ${env.DOCKER_IMAGE_NAME}:.*|image: ${env.DEPLOY_IMAGE}|g' k8s/worker.yml"

                    // Application des changements
                    sh "kubectl apply -f k8s/api.yml"
                    sh "kubectl apply -f k8s/worker.yml"

                    // Attente de la mise à jour effective (Rollout)
                    // Timeout de 60s pour éviter de bloquer le pipeline indéfiniment si ça plante
                    timeout(time: 60, unit: 'SECONDS') {
                        sh "kubectl rollout status deployment/nmap-api"
                        sh "kubectl rollout status deployment/nmap-worker"
                    }
                }
            }
        }
    }

    // Étape de nettoyage (se lance toujours, succès ou échec)
    post {
        always {
            script {
                // Supprime l'image locale pour libérer de la place sur le serveur Jenkins
                // On vérifie d'abord si la variable existe pour éviter une erreur
                if (env.DEPLOY_IMAGE) {
                    sh "docker rmi ${env.DEPLOY_IMAGE} || true"
                    sh "docker logout || true"
                }
            }
        }
    }
}