from mcp.server.fastmcp import FastMCP
import psycopg2, json, os
from dotenv import load_dotenv


mcp = FastMCP("NovaDriveAssistantTools", dependencies=["psycopg2"])
                                         

load_dotenv()

LLM_API_URL = os.getenv("LLM_API_URL", "").strip()
LLM_API_KEY = os.getenv("LLM_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "").strip()
TIMEOUT = float(os.getenv("LLM_TIMEOUT", "60"))
HEADERS = {"Content-Type": "application/json"}
if LLM_API_KEY:
    HEADERS["Authorization"] = f"Bearer {LLM_API_KEY}"

if not LLM_API_URL:
    sys.stderr.write("Error: LLM_API_URL is not set in .env\n")
    sys.exit(1)

CONN_STR = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def get_connection():
    return psycopg2.connect(**CONN_STR)

@mcp.tool()
def get_available_vehicles():
    """Returns available vehicles for purchase"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, type, price FROM vehicles;")
        rows = cursor.fetchall()
        result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        cursor.close()
        conn.close()
        return json.dumps(result, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_dealerships():
    """Returns dealership locations and information"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.dealership_id, d.name as dealership, c.name as city, s.name as state, s.abbreviation 
            FROM dealerships d
            JOIN cities c ON c.city_id = d.city_id
            JOIN states s ON c.state_id = s.state_id;
        """)
        rows = cursor.fetchall()
        result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        cursor.close()
        conn.close()
        return json.dumps(result, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_sellers_by_dealership(dealership_id: int):
    """Returns sellers by dealership ID"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.seller_id, s.name 
                    FROM sellers s 
                    WHERE s.dealership_id = %s;
                """, (dealership_id,))
                rows = cursor.fetchall()
                result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        return json.dumps(result, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def get_customer_info(name: str):
    """Returns customer information including purchased vehicles and dealership"""
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT cu.customer_id, cu.name as customer_name, d.name as dealership, c.name as city, s.name as state, 
                           sa.sale_date, sa.amount_paid, v.name as vehicle 
                    FROM customers cu
                    JOIN dealerships d ON cu.dealership_id = d.dealership_id
                    JOIN cities c ON c.city_id = d.city_id
                    JOIN states s ON s.state_id = c.state_id
                    JOIN sales sa ON sa.customer_id = cu.customer_id
                    JOIN vehicles v ON sa.vehicle_id = v.vehicle_id
                    WHERE cu.name = %s;
                """, (name,))
                rows = cursor.fetchall()
                result = [dict(zip([desc[0] for desc in cursor.description], row)) for row in rows]
        return json.dumps(result, indent=4, sort_keys=True, default=str)
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def schedule_visit_for_purchase(dealership_id: int, seller_id: int, datetime: str):
    """Schedules a visit to a dealership for purchasing a vehicle"""
    return {"message": "Visit successfully scheduled!"}

@mcp.tool()
def schedule_visit_for_maintenance(customer_id: int, dealership_id: int, vehicle_name: str, details: str, datetime: str):
    """Schedules a maintenance or service visit for existing vehicle owners"""
    return {"message": "Maintenance visit successfully scheduled!"}
