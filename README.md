# Web Server CRUD
Um web server para acessar e manipular um banco de dados com operações CRUD através do navegador.

O website acessa o banco de dados contendo nomes de restaurantes e os mostra na página `localhost:8080/restaurants`<br>
A partir dessa página é possível adicionar novos restaurantes ao banco de dados, editá-los e excluí-los.

## Requerimentos
- [Python 3](https://www.python.org/downloads/release/python-371/)
- [SQLAlchemy](https://www.sqlalchemy.org/) - Use o comando `pip install sqlalchemy` para instalar
- [Vagrant](https://www.vagrantup.com) - Ambiente de desenvolvimento - 
Baixe o arquivo com a máquina configurada [aqui](https://d17h27t6h515a5.cloudfront.net/topher/2017/June/5948287e_fsnd-virtual-machine/fsnd-virtual-machine.zip)
- [Virtual Box](https://www.virtualbox.org/wiki/Downloads) - Para rodar a VM vagrant

É recomendado utilizar a máquina virtual como ambiente de desenvolvimento, 
mas caso prefira executar na própria máquina não é necessário instalar o virtualbox, nem baixar o vagrant.

## Executando

Coloque os arquivos dentro da pasta `vagrant` do arquivo baixado.

Com a pasta vagrant aberta em um terminal insira o comando `vagrant up` para ligar a máquina virtual, em seguida o comando
`vagrant ssh` para fazer o login na máquina.

Vá até a pasta compartilhada com o comando `cd /vagrant`.

E execute o arquivo python com `python webserver.py` ou `python3 webserver.py`

Agora você é possível acessar o endereço `localhost:8080/restaurants` através do web browser acessando e manipulando os dados do banco de dados.
