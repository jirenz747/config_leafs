### INSTALLATION for Debian 9.8


Создаем пользователя от которого будет все работать:
```
adduser --gecos "" ubuntu
usermod -aG sudo ubuntu
su ubuntu
```

Устанавливаем необходимые пакеты:
```
sudo apt install git python3 python3-pip python3-venv python3-flask libsasl2-dev python-dev libldap2-dev libssl-dev 
```

Клонируем репозиторий:
```
git clone https://github.com/jirenz747/config_leafs.git
cd dc_config_leafs/
```
Создаем вируальное окружение и активируем его:
```
python3 -m venv env
source env/bin/activate
```

Устанавливаем дополнительные пакеты через pip:
```
pip install --upgrade-pip
pip install -r requirements.txt
```
Указываем flask откуда начинается наше приложение:
```
echo "export FLASK_APP=config_leafs.py" >> ~/.profile
```

Перезапускаем вируальное окружение:
```
deactivate
source env/bin/activate
```
Запускаем приложение.
```
flask run
```
После успешного запуска приложения продолжаем дальше.



Подготавливаем конфигурационный файл:
```
vim app/config.yml
```

Задаем пользователя и пароль для доступа к сетевому оборудованию:
```
  authentication_network_device:
    username: 'admin'
    password: 'admin'

```

Если мы не хотим использовать аутентификацию ldap, то задаем параметр No и указываем логин и пароль:
```
  authentication_web:
    plain_text_password:
      username: 'admin'
      password: 'admin'
      
    ldap:
      use: 'No'

```

Для добавления доменной аутентификации прописываем свои значения:
```
      domain_groups: -- список групп, которые будут иметь доступ до данной тулзы
        - 'NetworksAdmins'
        - 'ServersAdmins'
      ldap_server: 'ldap://yourdomain.com'
      ldap_domain: 'yourdomain.com'
      base_dn: 'DC=yourdomain,DC=com'
```

Для добавления устройства, которому будет осуществлятся доступ описывается ниже:
```
M1:                             -- Указываем локацию
  Rack_1:                       -- Указываем номер стойки или название свитча
    device_ip: '192.168.1.1'    -- IP
    device_name: 'm1_l1'       -- hostname
    device_count: '2'           -- количество устройств в стеке
    port_count: '48'            -- количество портов
    exclude_ports:              -- указываем список портов, к которым не будет доступа для настройки
      - 'ge-1/0/47'
      - 'ge-0/0/47'
      - 'xe-1/0/0'
      - 'xe-0/0/1'
  
  Rack_2:
    device_ip: '192.168.1.2'
    device_name: 'm1_l2'
    device_count: '1'
    port_count: '48'
    exclude_ports:              -- В данном случае можно будет настраивать все порты 
      - 'None'

```


### Продолжаем полноценное развертывание


```
sudo apt install supervisor nginx
```

Настраиваем супервизор
sudo vim /etc/supervisor/conf.d/config_leafs.conf
```
[program:config_leafs]
command=/home/ubuntu/dc_config_leafs/env/bin/gunicorn -b localhost:8000 -w 4 config_leafs:app
directory=/home/ubuntu/dc_config_leafs
user=ubuntu
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
```

### Настройка nginx

Генерируем самоподписанные сертификаты:
```
mkdir certs
openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -keyout certs/key.pem -out certs/cert.pem
```
Настравиваем сервер nginx
```
sudo rm /etc/nginx/sites-enabled/default
vim /etc/nginx/sites-enabled/config_leafs

```

```
server {
    # прослушивание порта 80 (http)
    listen 80;
    server_name _;
    location / {
        # перенаправлять любые запросы на один и тот же URL-адрес, как на https
        return 301 https://$host$request_uri;
    }
}
server {
    # прослушивание порта 443 (https)
    listen 443 ssl;
    server_name _;

    # расположение self-signed SSL-сертификата
    ssl_certificate /home/ubuntu/dc_config_leafs/certs/cert.pem;
    ssl_certificate_key /home/ubuntu/dc_config_leafs/certs/key.pem;

    # запись доступа и журналы ошибок в /var/log
    access_log /var/log/dc_config_leafs.log;
    error_log /var/log/dc_config_leafs.log;

    location / {
        # переадресация запросов приложений на сервер gunicorn
        proxy_pass http://localhost:8000;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        # обрабатывать статические файлы напрямую, без пересылки в приложение
        alias /home/ubuntu/dc_config_leafs/app/static;
        expires 30d;
    }
}
```

Перезапускаем nginx
```
sudo service nginx reload
```
