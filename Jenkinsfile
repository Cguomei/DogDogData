# Jenkinsfile - Flask 项目 CI/CD 流水线

// 声明式流水线
pipeline {
    agent any
    
    // 工具配置
    tools {
        python 'Python-3.9'  // 需在 Jenkins 全局工具配置中定义
    }
    
    // 环境变量
    environment {
        PYTHONUNBUFFERED = '1'
        PYTHONDONTWRITEBYTECODE = '1'
        REPORT_DIR = 'Test/reports'
        FLASK_APP = 'app.py'
        
        // 数据库配置（从 Jenkins Credentials 获取）
        DB_HOST = credentials('mysql-host')
        DB_USER = credentials('mysql-user')
        DB_PASSWORD = credentials('mysql-password')
        DB_NAME = credentials('mysql-database')
    }
    
    // 触发器配置
    triggers {
        // 定时触发（每周一到周五早上 9 点执行）
        cron('0 9 * * 1-5')
        
        // 代码提交后触发（需配置 Git hook）
        // pollSCM('H/5 * * * *')  // 每 5 分钟检查一次
    }
    
    // 参数化构建
    parameters {
        string(name: 'BRANCH', defaultValue: 'main', description: 'Git 分支')
        booleanParam(name: 'RUN_UI_TESTS', defaultValue: true, description: '是否运行 UI 测试')
        booleanParam(name: 'RUN_PERF_TESTS', defaultValue: false, description: '是否运行性能测试')
        choice(name: 'NOTIFY_TYPE', choices: ['ALWAYS', 'FAILURE', 'SUCCESS'], description: '通知策略')
    }
    
    // 流水线阶段
    stages {
        // 阶段 1: 代码检出
        stage('Checkout') {
            steps {
                echo '📦 正在检出代码...'
                checkout scm
                script {
                    env.GIT_COMMIT = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
                    env.GIT_BRANCH = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()
                    echo "✅ 代码检出完成 - 分支：${env.GIT_BRANCH}, 提交：${env.GIT_COMMIT}"
                }
            }
        }
        
        // 阶段 2: 环境准备
        stage('Setup Environment') {
            steps {
                echo '🔧 正在配置测试环境...'
                script {
                    // 创建虚拟环境
                    sh '''
                        python -m venv venv
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        python --version
                    '''
                    
                    // 创建报告目录
                    sh '''
                        mkdir -p ${REPORT_DIR}
                        mkdir -p logs
                    '''
                    
                    echo '✅ 环境配置完成'
                }
            }
        }
        
        // 阶段 3: 安装依赖
        stage('Install Dependencies') {
            steps {
                echo '📥 正在安装依赖包...'
                script {
                    sh '''
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        pip install --upgrade pip
                        pip install -r requirements.txt
                        pip install pytest-html pytest-xdist pytest-cov
                    '''
                    echo '✅ 依赖安装完成'
                }
            }
        }
        
        // 阶段 4: 代码质量检查
        stage('Code Quality Check') {
            steps {
                echo '🔍 正在进行代码质量检查...'
                script {
                    // 可选：安装 flake8 和 black
                    sh '''
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        pip install flake8 black
                        
                        # 代码格式检查
                        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        
                        # 代码格式化检查
                        black --check .
                    '''
                    echo '✅ 代码质量检查通过'
                }
            }
        }
        
        // 阶段 5: 数据库初始化
        stage('Initialize Database') {
            steps {
                echo '💾 正在初始化数据库...'
                script {
                    sh '''
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        python init_db.py
                    '''
                    echo '✅ 数据库初始化完成'
                }
            }
        }
            
        // 阶段 6: 执行测试
        stage('Run Tests') {
            parallel {
                // 并行执行单元测试
                stage('Unit Tests') {
                    steps {
                        echo '🧪 正在执行单元测试...'
                        script {
                            sh '''
                                source venv/bin/activate || .\\venv\\Scripts\\activate
                                python -m pytest Test/test_*.py \
                                    -v \
                                    --tb=short \
                                    --html=${REPORT_DIR}/unit_test_report.html \
                                    --self-contained-html \
                                    --junitxml=${REPORT_DIR}/unit_test_junit.xml \
                                    -s
                            '''
                        }
                    }
                    post {
                        always {
                            // 保存测试报告
                            junit allowEmptyResults: true, testResults: '${REPORT_DIR}/unit_test_junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '${REPORT_DIR}',
                                reportFiles: 'unit_test_report.html',
                                reportName: '单元测试报告'
                            ])
                        }
                    }
                }
                
                // 并行执行接口测试
                stage('API Tests') {
                    when {
                        expression { return true }  // 总是执行
                    }
                    steps {
                        echo '🔌 正在执行接口测试...'
                        script {
                            sh '''
                                source venv/bin/activate || .\\venv\\Scripts\\activate
                                python -m pytest Test/test_api.py Test/test_auth.py Test/test_routes.py \
                                    -v \
                                    --tb=short \
                                    --html=${REPORT_DIR}/api_test_report.html \
                                    --self-contained-html \
                                    --junitxml=${REPORT_DIR}/api_test_junit.xml \
                                    -n 4 \
                                    -s
                            '''
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: '${REPORT_DIR}/api_test_junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '${REPORT_DIR}',
                                reportFiles: 'api_test_report.html',
                                reportName: '接口测试报告'
                            ])
                        }
                    }
                }
                
                // 条件执行 UI 测试
                stage('UI Tests') {
                    when {
                        expression { return params.RUN_UI_TESTS }
                    }
                    steps {
                        echo '🎨 正在执行 UI 自动化测试...'
                        script {
                            sh '''
                                source venv/bin/activate || .\\venv\\Scripts\\activate
                                python -m pytest Test/test_routes.py \
                                    -v \
                                    --tb=short \
                                    --html=${REPORT_DIR}/ui_test_report.html \
                                    --self-contained-html \
                                    --junitxml=${REPORT_DIR}/ui_test_junit.xml \
                                    -s
                            '''
                        }
                    }
                    post {
                        always {
                            junit allowEmptyResults: true, testResults: '${REPORT_DIR}/ui_test_junit.xml'
                            publishHTML(target: [
                                allowMissing: true,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: '${REPORT_DIR}',
                                reportFiles: 'ui_test_report.html',
                                reportName: 'UI 测试报告'
                            ])
                        }
                    }
                }
            }
            
            // 测试后处理
            post {
                always {
                    echo '📊 测试执行完成，生成汇总报告...'
                }
                success {
                    echo '✅ 所有测试通过！'
                }
                failure {
                    echo '❌ 部分测试失败，请检查报告'
                }
            }
        }
        
        // 阶段 7: 生成覆盖率报告
        stage('Coverage Report') {
            steps {
                echo '📈 正在生成代码覆盖率报告...'
                script {
                    sh '''
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        python -m pytest Test/ \
                            --cov=. \
                            --cov-report=html:${REPORT_DIR}/coverage_html \
                            --cov-report=xml:${REPORT_DIR}/coverage.xml \
                            --cov-report=term-missing
                    '''
                }
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '${REPORT_DIR}/coverage_html',
                        reportFiles: 'index.html',
                        reportName: '代码覆盖率报告'
                    ])
                    cobertura autoUpdateHealth: true, 
                              autoUpdateStatus: true, 
                              conditionalProbabilityRanges: '0.7,0.8,0.9,1.0',
                              failNoReports: false, 
                              failUnhealthy: false, 
                              failUnstable: false, 
                              lineCoverageTargets: '80,0,0',
                              methodCoverageTargets: '80,0,0',
                              onlyStableBuilds: false, 
                              packageCoverageTargets: '80,0,0',
                              sourceEncoding: 'UTF-8',
                              zoomCoverageChart: false
                }
            }
        }
        
        // 阶段 8: 打包部署（可选）
        stage('Build & Deploy') {
            when {
                branch 'main'  // 仅 main 分支执行部署
            }
            steps {
                echo '📦 正在打包应用...'
                script {
                    sh '''
                        source venv/bin/activate || .\\venv\\Scripts\\activate
                        pip install pyinstaller
                        # 可选：打包为可执行文件
                        # pyinstaller --onefile app.py
                    '''
                    
                    // 归档构建产物
                    archiveArtifacts artifacts: '**/*.py, **/*.html, **/*.css, **/*.js', 
                                       fingerprint: true,
                                       allowEmptyArchive: true
                }
            }
        }
    }
    
    // 流水线结束后的操作
    post {
        always {
            echo '🎉 流水线执行完成'
            
            // 清理工作空间
            cleanWs(
                cleanWhenNotBuilt: false,
                deleteDirs: true,
                disableDeferredWipeout: true,
                patterns: [
                    [pattern: '**/*.pyc', type: 'INCLUDE'],
                    [pattern: '**/__pycache__/**', type: 'INCLUDE'],
                    [pattern: 'venv/**', type: 'INCLUDE']
                ]
            )
        }
        
        success {
            echo '✅ 构建成功！'
            
            // 发送邮件通知（如果配置了邮件）
            emailext (
                subject: "✅ 构建成功：${env.JOB_NAME} [${env.BUILD_NUMBER}]",
                body: """构建成功！
                
分支：${env.GIT_BRANCH}
提交：${env.GIT_COMMIT}
构建号：${env.BUILD_NUMBER}
查看报告：${env.BUILD_URL}""",
                to: "${env.NOTIFY_EMAIL}",
                when: params.NOTIFY_TYPE == 'ALWAYS' || params.NOTIFY_TYPE == 'SUCCESS'
            )
        }
        
        failure {
            echo '❌ 构建失败！'
            
            // 发送失败通知
            emailext (
                subject: "❌ 构建失败：${env.JOB_NAME} [${env.BUILD_NUMBER}]",
                body: """构建失败！
                
分支：${env.GIT_BRANCH}
提交：${env.GIT_COMMIT}
构建号：${env.BUILD_NUMBER}
查看报告：${env.BUILD_URL}
错误日志：${env.BUILD_URL}console""",
                to: "${env.NOTIFY_EMAIL}",
                attachLog: true,
                when: params.NOTIFY_TYPE == 'ALWAYS' || params.NOTIFY_TYPE == 'FAILURE'
            )
        }
        
        unstable {
            echo '⚠️ 构建不稳定（部分测试失败）'
        }
    }
}
