from flask import Flask, jsonify,abort,make_response,url_for,request
import smtplib
import time
from sqlalchemy import  Table, MetaData, create_engine, Column, Integer, String,  ForeignKey
from sqlalchemy.orm import mapper,sessionmaker
from sqlalchemy.ext.declarative import declarative_base
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def make_connect():
    engine = create_engine('postgresql+psycopg2://postgres:Werserg2294@127.0.0.1:5433/conference_room',pool_pre_ping=True)
    connection = engine.connect()
    return connection, engine



config = configparser.ConfigParser()
config.read("settings.ini")
app = Flask(__name__)

host = config.get("Settings", "host")
Login = ''
role = ''
from_addrq = config.get("Settings", "from_addr")
users = [("login",'passw','1')]

metadata = MetaData(bind=make_connect()[1])

Base = declarative_base()

class User(Base):
    __table__ = Table('user_info', metadata, autoload=True,
    id_user = Column(Integer, autoincrement=True))

    def __init__(self,id_user, login, password,fio,root_id):
        self.id_user = id_user
        self.User_login = login
        self.User_password = password
        self.FIO = fio
        self.root_id = root_id

    def __repr__(self):
        return "<User('%s', '%s','%s', '%s', '%s')>" % (self.id_user, self.User_login, self.User_password, self.FIO, self.root_id)



class all_room(Base):
    __table__ = Table('all_rooms', metadata, autoload=True,
                      room_id = Column(Integer, primary_key= True))

    def __init__(self,name, adress, chairs, projector, reserv_start, room_id, reserv_finish, board):
        self.name = name
        self.adress = adress
        self.chairs = chairs
        self.projector = projector
        self.board = board
        self.reserv_start = reserv_start
        self.room_id = room_id
        self.reserv_finish = reserv_finish

    def __repr__(self):
        return "<All ROOMS ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s')>"%(self.name,self.adress,self.chairs,self.projector,self.board,self.reserv_start,self.room_id,self.reserv_finish )


class rooms_info(Base):
    __table__ = Table('room_info', metadata, autoload=True,
                      id_str= Column(Integer, primary_key= True))

    def __init__(self,  projector, reserv_start, room_id, reserv_finish, name, adress, chairs, board, id_str, reserver):
        self.projector = projector
        self.reserv_start = reserv_start
        self.room_id = room_id
        self.reserv_finish = reserv_finish
        self.name = name
        self.adress = adress
        self.chairs = chairs
        self.board = board
        self.reserver = reserver



    def __repr__(self):
        return "<info ('%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s')>" % (
            self.projector,  self.reserv_start, self.room_id, self.reserv_finish,
            self.name, self.adress, self.chairs, self.board,  self.reserver)







class sql_post():
    def __init__(self):
        self.db_host = ''
        self.Session = sessionmaker(bind=make_connect()[1])

    def len_user(self):
        session = self.Session()
        len_usser = len(session.query(User).all())
        return len_usser

    def get_user(self, **kwargs):
        login = kwargs['Login']
        password = kwargs['Password']
        session = self.Session()
        user_info = session.query(User).filter_by(User_login=login).first()
        print('login_select:"{}"|||||login_json:"{}"|||sovpadaut:{}\npass_select:"{}"|||||pass_json:"{}"|||sovpadaut:{}'.format(user_info.User_login,login,login==user_info.User_login,user_info.User_password,password,password==user_info.User_password))
        try:
            if user_info.User_login != login or user_info.User_password != password:
                return 404
            else:
                return user_info.root_id
        except:
            return 404



    def create_user(self,**kwargs):
        id_user =  kwargs['id_user']
        login = kwargs['Login']
        password = kwargs['Password']
        fio = kwargs['fio']
        root_id = kwargs['root_id']
        session = self.Session()
        try:
            new_User = User(id_user, login, password, fio, root_id)
            session.add(new_User)
            session.commit()
            return True
        except :
            return False


    def get_all_rooms(self):
        session = self.Session()
        room = session.query(all_room).first()
        return room


    def get_room_info(self,room_id):
        session = self.Session()
        id=room_id
        info = session.query(rooms_info).filter_by(room_id=id).all()
        return info




@app.route('/roomreserv/Login', methods=['POST'])
def login_():
    '''curl -i -H "Content-Type: application/json" -X POST -d "{\"Login\": \"serg\", \"Password\": \"11221\"}" http://127.0.0.1:5000/roomreserv/Login'''
    if not request.json or not 'Login' or not 'Password' in request.json:
        abort(400)
    sql_ = sql_post()
    login = request.json.get('Login')
    password = request.json.get('Password')
    root_id = sql_.get_user(Login=login, Password=password)
    if root_id == 404:
        return jsonify({'messg': 'oopss'}), 201
    else:
        return jsonify({'user': login,'root_id':root_id}), 201

@app.route('/roomreserv/new_user', methods=['POST'])
def new_user():
    '''curl -i -H "Content-Type: application/json" -X POST -d "{\"Login\": \"vasia\", \"Password\": \"11221\", \"FIO\": \"vasia\",\"root_id\": \"0\" }" http://127.0.0.1:5000/roomreserv/new_user'''
    if not request.json or not 'Login' or not 'Password'or not 'root_id' or not 'FIO' in request.json:
        abort(400)
    sql_ = sql_post()
    login = request.json.get('Login')
    password = request.json.get('Password')
    fio = request.json.get('FIO')
    root_id = request.json.get('root_id')
    k=sql_.len_user()+1
    is_true = sql_.create_user(id_user = k,Login=login,Password=password,fio=fio,root_id=root_id)
    if is_true == True:
        return jsonify({'user': login,'root_id':root_id, 'mess': 'user "{}" was created'.format(fio)}), 201
    else:
        return jsonify({'user': login,'root_id':root_id}), 201


@app.route('/roomreserv/all_room', methods=['GET'])
def get_all_room():
    sql_ = sql_post()
    room = sql_.get_all_rooms()
    rooms=[]
    k=0
    for i in room:
        rooms.append({
        'name':i.name,
        'adress':i.adress,
        'chairs':i.chairs,
        'projector':i.projector,
        'reserv_start':i.reserv_start,
        'room_id':i.room_id,
        'reserv_finish':i.reserv_finish,
        'board':i.board
        } )
        k+=1
    return jsonify({'room':rooms})





@app.route('/roomreserv/room-info/<int:room_id>', methods=['GET'])
def room_info(room_id):
    sql_=sql_post()
    info =sql_.get_room_info(room_id)
    print(info)
    print(info[0])
    all_info={
        'name':info[0].name,
        'adress': info[0].adress,
        'chairs': info[0].chairs,
        'projector': info[0].projector,
        'room_id': info[0].room_id,
        'board': info[0].board,
        'reserv_info':[]}
    input(all_info['reserv_info'])
    for i in info:
        all_info['reserv_info'].append({'reserv_start': i.reserv_start,
                                        'reserv_finish': i.reserv_finish,
                                        'reserver': i.reserver})
    return jsonify({'room Info': all_info})



@app.route('/roomreserv/create-room', methods=['POST'])
def create_new_room():
    sql_ = sql_post()
    name = request.json.get('name')
    adress = request.json.get('adress')




if __name__ == '__main__':
    #app.run(debug=True)
    app.run()