import serial
import datetime
import common
from common import AlarmStatus, EventType, Settings, ZoneInfo, User, EventLog
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Create the serial device.
ser = serial.Serial('/dev/ttyUSB0', 115200)
# Create the database engine.
engine = create_engine(common.SQLITE_URL) #TODO: Might be good to have an actual config file...
DBSession = sessionmaker(bind=engine)
db_session = DBSession()

# Keep track if there is one or more events in progress
bOngoingEvent = False

def main():                
    try:
        debug_print("Listening...")
        bIsFirstMessage = True
        while True:
            # Get the line from the AD2USB.
            strMessage = ser.readline().decode("utf-8")
            # If this is the first message, just dump it because we might not have a full string.
            if bIsFirstMessage == False:
                # Ignore the weird RFX strings...
                if strMessage[0:4] != "!RFX": 
                    parseMessage(strMessage)
            bIsFirstMessage = False
    except KeyboardInterrupt:
        ser.close()
        pass

# Argument example:[1000000100000000----]
def parseMessage( strMessage ):

    global bOngoingEvent

    debug_print(strMessage)
    strSettings, strZone, strRawPanelBinary, strKeypadMessage = strMessage.split(",")

    settings = parseSettings(strSettings) 
    db_session.add(settings)

    # Check to see if a zone has been triggered.
    # TODO: Need to determine why zone 8 is the default...
    if settings.armed_status != AlarmStatus.Ready.value and strZone != "008":
        bOngoingEvent = True

        # Check to see if this row is already triggered.
        curZoneInfo = db_session.query(ZoneInfo).get(int(strZone))
        if(curZoneInfo.triggered == 0):
            debug_print("Event started for zone " + strZone)
            # Set the appropriate zone to triggered
            db_session.query(ZoneInfo).filter_by(id = curZoneInfo.id).update({ZoneInfo.triggered: 1})
        
            # Log the event
            eventLog = EventLog()
            eventLog.zone_id = curZoneInfo.id
            eventLog.type = EventType.Fault.value
            db_session.add(eventLog)    
    
    # Otherwise, ensure all zones are not triggered
    elif(bOngoingEvent):
        bOngoingEvent = False
        debug_print("Events ending")
        # Set all zone info triggers to 0
        db_session.query(ZoneInfo).update({ZoneInfo.triggered: 0})
        # Update the end timestamps for all rows that have null end times.
        db_session.query(EventLog).filter(EventLog.end_time.is_(None)).update({EventLog.end_time:  datetime.datetime.now()})

    db_session.commit()

# Parse the settings field
def parseSettings( strSettings ):
    settings = Settings()

    # Clear the table before adding the new settings
    db_session.query(Settings).delete()
    db_session.commit()    
    
    # Note: strSettings[0] is a bracket character
    # Determine what mode the system is currently in.
    if strSettings[1] == "1":
        settings.armed_status = AlarmStatus.Ready.value        
    elif strSettings[2] == "1":
        settings.armed_status = AlarmStatus.ArmedAway.value
    elif strSettings[3] == "1":
        settings.armed_status = AlarmStatus.ArmedStay.value
    else:
        settings.armed_status = AlarmStatus.Fault.value
    
    settings.backlight = strSettings[4]     
    settings.programming_mode = strSettings[5]
    settings.beep_count = strSettings[6]
    settings.zone_bypassed = strSettings[7]
    settings.ac_power = strSettings[8]
    settings.chime_mode = strSettings[9]
    settings.alarm_occurred = strSettings[10]
    settings.alarm_bell = strSettings[11]
    settings.battery_low = strSettings[12]
    settings.entry_delay = strSettings[13]
    settings.fire_alarm = strSettings[14]
    settings.check_zone = strSettings[15]
    settings.perimeter_only = strSettings[16]

    return settings

def debug_print( strPrint ):    
    if common.DEBUG:
        print(strPrint)

if __name__ == '__main__':
    main()
