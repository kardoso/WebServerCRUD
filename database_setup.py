#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# importar classes para escrever o mapeador
from sqlalchemy import Column, ForeignKey, Integer, String
# daclarative_base é usada na configuração e no código de classe
from sqlalchemy.ext.declarative import declarative_base
# para criar relação de chave estrangeira, usada também no mapeador
from sqlalchemy.orm import relationship
# usada no fim do arquivo para configuração
from sqlalchemy import create_engine


Base = declarative_base()

# Classes


class User(Base):
    # Tabela
    __tablename__ = 'user'

    # Mapeadores
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Restaurant(Base):
    # Tabela
    __tablename__ = 'restaurant'

    # Mapeadores
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


class MenuItem(Base):
    # Tabela
    __tablename__ = 'menu_item'

    # Mapeadores
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(250))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))
    restaurant = relationship(Restaurant)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'course': self.course,
            'price': self.price,
        }


# Configuração

# indicar o banco de dadaos que será usado
engine = create_engine('sqlite:///restaurantmenu.db')
# acessar o banco de dados e adicionar as tabelas criadas
Base.metadata.create_all(engine)
