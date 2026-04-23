# 监控系统使用说明

## 📊 组件说明

本监控系统包含以下组件：

- **Prometheus**: 指标收集和存储
- **Grafana**: 数据可视化和看板
- **Node Exporter**: 系统指标采集
- **Flask App**: 应用指标导出

## 🚀 快速启动

### 1. 启动监控服务

```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

### 2. 访问服务

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - 用户名: `admin`
  - 密码: `admin123`

### 3. 查看指标

访问 Flask 应用的指标端点：
```bash
curl http://localhost:5000/metrics
```

## 📈 Grafana 看板

### 导入看板

1. 登录 Grafana
2. 进入 Dashboards → Import
3. 上传 `monitoring/grafana/dashboards/flask_monitoring.json`
4. 选择 Prometheus 数据源
5. 点击 Import

### 看板内容

- HTTP 请求速率
- 请求延迟（P95）
- 内存使用率
- CPU 使用率
- 业务指标趋势（注册/登录）

## 🔔 告警规则

已配置的告警规则：

### 应用告警
- **HighErrorRate**: HTTP 5xx 错误率 > 5%
- **HighRequestLatency**: P95 延迟 > 1s
- **AppDown**: 应用宕机

### 系统告警
- **HighCPUUsage**: CPU 使用率 > 80%
- **HighMemoryUsage**: 内存使用率 > 85%
- **LowDiskSpace**: 磁盘空间 < 15%

### 业务告警
- **DatabaseConnectionFailed**: 数据库连接失败
- **UserRegistrationDrop**: 用户注册量异常下降

## 🛠️ 配置说明

### Prometheus 配置

编辑 `monitoring/prometheus.yml`：

```yaml
scrape_configs:
  - job_name: 'flask_app'
    static_configs:
      - targets: ['host.docker.internal:5000']
```

### 告警规则

编辑 `monitoring/alerts.yml` 添加或修改告警规则。

## 📝 自定义指标

在代码中使用装饰器：

```python
from utils.monitoring import track_user_registration

@api_bp.route('/api/register', methods=['POST'])
@track_user_registration
def register():
    # 你的代码
    pass
```

或手动记录：

```python
from utils.monitoring import CHART_GENERATION_COUNT

CHART_GENERATION_COUNT.labels(chart_type='scatter').inc()
```

## 🔧 常用命令

### 查看容器状态
```bash
docker-compose -f docker-compose.monitoring.yml ps
```

### 查看日志
```bash
docker-compose -f docker-compose.monitoring.yml logs -f prometheus
docker-compose -f docker-compose.monitoring.yml logs -f grafana
```

### 停止服务
```bash
docker-compose -f docker-compose.monitoring.yml down
```

### 重启服务
```bash
docker-compose -f docker-compose.monitoring.yml restart
```

## ⚠️ 注意事项

1. **生产环境**请修改 Grafana 默认密码
2. **数据持久化**已通过 Docker volumes 配置
3. **时区设置**默认为 UTC，可在 Grafana 中修改
4. **资源限制**建议为 Prometheus 和 Grafana 设置内存限制

## 📚 相关文档

- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [Prometheus Flask Exporter](https://github.com/rycus86/prometheus_flask_exporter)
