from langchain_core.tools import tool
from my_sql import DBConnector

db = DBConnector.instance()


# ----- Tools for Booking Operations -----

@tool
def create_booking(name: str, contact: str, start_date: str, end_date: str, room_id: int) -> str:
    """
    Save user booking
    Args:
        name (str): user name
        contact (str): user contact
        start_date (str): booking start date
        end_date (str): booking end date
        room_id (int): room id for booking
    Returns:
        str: _description_
    """
    query_insert = f"""
    INSERT INTO Bookings (room_id, check_in_date, check_out_date, total_price, booking_status, name, contact)
    VALUES ({room_id}, '{start_date}', '{end_date}',(SELECT price FROM Rooms WHERE room_id = {room_id}) * DATEDIFF('{end_date}', '{start_date}'), 
    'confirmed', '{name}', '{contact}');
    """
    status = db.insert(query_insert)
    print("create: ", status, sep="\n")
    if status:
        return f"Booking confirmed for {name} ({contact}) from {start_date} to {end_date}."
    return f"Booking cannot be done."


@tool
def check_availability(start_date: str, end_date: str, capacity: int) -> str:
    """
    Rooms avaliable or not
    Args:
        start_date (str): booking start date.
        end_date (str): booking end date.
        capacity  (int): number of people in room.
    Returns:
        str: _description_
    """
    query = f"""
    SELECT type, MIN(room_id) AS room_id, MIN(capacity) AS capacity,MIN(price) AS price
    FROM Rooms
    WHERE room_id NOT IN (
        SELECT room_id
        FROM Bookings
        WHERE (check_in_date <= '{start_date}' AND check_out_date >= '{end_date}') 
        AND booking_status = 'confirmed'
    )
    AND capacity >= {capacity}
    GROUP BY type;
    """
    result = db.query(query)
    print("availability: ", result, sep="\n")
    if len(result) > 0:
        formatted_data = "\n".join(
            [f"{row[0]},{row[1]},{row[2]},Per day {row[3]}" for row in result])
        return f"Rooms are available. \n" + formatted_data
    return f"Rooms are not available from {start_date} to {end_date}."


@tool
def check_booking(name: str, contact: str) -> str:
    """
    Check user booking avaliable or not
    Args:
        name (str): user name
        contact (str): user contact

    Returns:
        str: Check Booking
    """
    query = f"""
    SELECT * FROM Bookings WHERE name = '{name}' AND contact = '{contact}' AND booking_status = 'confirmed';
    """
    result = db.query(query)
    print("booking: ", result, sep="\n")
    if len(result) > 0:
        formatted_data = ".\n".join(
                [f"{row[0]},{row[1]},{row[2]},Per day {row[3]}" for row in result])
        return formatted_data
    return "Cannot find the booking."


@tool
def update_booking(name: str, contact: str, start_date: str, end_date: str, room_id: int) -> str:
    """
    Update user booking
    Args:
        name (str): user name
        contact (str): user contact
        start_date (str): booking start date
        end_date (str): booking end date
        room_id (int): room id for booking
    Returns:
        str: Booking confied or not
    """
    
    query = f"""
        UPDATE Bookings
    SET 
        check_in_date = '2025-05-02',
        check_out_date = '2025-05-06',
        total_price = (SELECT price FROM Rooms WHERE room_id = {room_id}) * DATEDIFF('{end_date}', '{start_date}'),
        room_id = {room_id}
    WHERE name = '{name}'
    AND contact = '{contact}'; 
    """
    status = db.update(query)
    print("update: ", status, sep="\n")
    if status:
        return f"Booking updated for {name} from {start_date} to {end_date}."
    return 'Booking updated failed.'


@tool
def cancel_booking(name: str, contact: str) -> str:
    """
    Cancel user booking
    Args:
        name (str): user name
        contact (str): user contact
    Returns:
        str: _description_
    """
    query = f"""
    UPDATE Bookings
    SET booking_status = 'canceled'
    WHERE name = '{name}'
    AND contact = '{contact}'
    """
    status = db.update(query)
    print("status: ", status, sep="\n")
    if status:
        return f"Booking canceled."
    return 'Booking cancalation failed.'


TOOLS = [
    create_booking,
    check_availability,
    check_booking,
    update_booking,
    cancel_booking
]
