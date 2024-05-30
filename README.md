# Dopany Airflow

Host : http://dopany-airflow.ddns.net:8080

## Airflow Test

```shell
path/to/your/local/repository > docker-compose up --build -d
```

### Image Info

![image](https://github.com/Dopany/DataPipeline-Airflow/assets/64184518/27c0959f-d2af-48ef-b2e6-a98234a5ef7c)


## SSH Info

**Port Mapping**
- webserver : 2220
- scheduler : 2221
- worker : 2222
- triggerer : 2223

**SSH Connect Example**

```
ssh username@dopany-airflow.ddns.net -p 2223
```
