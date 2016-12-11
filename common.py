# This file is for objects  that are common between AD2USBParser and the Flask application.
# TODO: Executing this file will create the database, which might be a little silly
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base


SQLITE_URL = "sqlite:////srv/app/HomeSecurity/home_security.db"
DEBUG = True

# TODO: Figure out how to get enums working with SQLAlchemy
class AlarmStatus(Enum):
    Ready = 0
    ArmedAway = 1
    ArmedStay = 2 
    Fault = 3   

# TODO: Will I actually be need this?
class EventType(Enum):
    Fault = 0

Base = declarative_base()

# Holds the alarm panel settings
class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key = True)
    armed_status = Column(Integer, nullable = False) # 0-2: Ready, Armed Away, Armed Home
    backlight = Column(Integer, nullable = False) # On or Off
    programming_mode = Column(Integer, nullable = False) # On or Off?
    beep_count = Column(Integer, nullable = False) # 0-7, number of beeps
    zone_bypassed = Column(Integer, nullable = False) # On or Off?
    ac_power = Column(Integer, nullable = False) # On or Off
    chime_mode = Column(Integer, nullable = False) # On or Off
    alarm_occurred = Column(Integer, nullable = False) # Cleared after second disarm
    alarm_bell = Column(Integer, nullable = False) # Cleared after first disarm
    battery_low = Column(Integer, nullable = False) # On or Off
    entry_delay = Column(Integer, nullable = False)
    fire_alarm = Column(Integer, nullable = False) # On or Off
    check_zone = Column(Integer, nullable = False)
    perimeter_only = Column(Integer, nullable = False)
        
# The current zone status
class ZoneInfo(Base):
    __tablename__ = 'zoneinfo'
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    triggered = Column(Integer, nullable = False)

# For logging
class EventLog(Base):
    __tablename__ = 'eventlog'
    id = Column(Integer, primary_key = True)
    zone_id = Column(Integer, ForeignKey(ZoneInfo.id), nullable = False)
    type = Column(Integer, nullable = False)
    start_time = Column(DateTime, nullable = False, default = func.now())
    end_time = Column(DateTime, nullable = True)

# Users
class User(Base):
    __tablename__ = 'users'    
    id = Column(Integer, primary_key = True)
    name = Column(String, nullable = False)
    level = Column(Integer, nullable = False, default = 0)
    password = Column(String, nullable = False)

    # Flask-Login functions
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous():
        return False

    def get_id(self):
        return self.id


# Creates the zones for the house if the table is empty, until something has been written to add them dynamically.
def zoneInit():
    if db_session.query(ZoneInfo).count() == 0:
        print("Initializing zones...")
        zone1 = ZoneInfo(id = 1, name = "Front Door", triggered = 0)
        zone2 = ZoneInfo(id = 2, name = "Garage Door", triggered = 0)
        zone3 = ZoneInfo(id = 3, name = "Back Door", triggered = 0)
        zone4 = ZoneInfo(id = 4, name = "Deck Door", triggered = 0)
        zone5 = ZoneInfo(id = 5, name = "Basement Motion", triggered = 0)
        zone6 = ZoneInfo(id = 6, name = "Kitchen Motion", triggered = 0)

        db_session.add(zone1)
        db_session.add(zone2)
        db_session.add(zone3)
        db_session.add(zone4)
        db_session.add(zone5)
        db_session.add(zone6)

        db_session.commit()

# Creates a default admin user if the table is empty, until something else replaces this
def adminInit():
    if db_session.query(User).count() == 0:
        print("Initializing admin user...")
        user = User()
        user.name = "admin"
        user.level = 1
        #user.password = bcrypt.hashpw("admin".encode('utf-8'), bcrypt.gensalt()) TODO: IMPLEMENT BCRYPT HERE
        user.password = "admin"
        db_session.add(user)
        db_session.commit()  

# Create the database and populate it with some defaults         
engine = create_engine(SQLITE_URL)
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
db_session = DBSession()
zoneInit()
adminInit()
