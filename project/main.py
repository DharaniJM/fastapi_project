import time
from fastapi import FastAPI, Form,Request
import psycopg2
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from psycopg2.extras import RealDictCursor 

templates =Jinja2Templates(directory="templates")

while True:
    try:
        conn=psycopg2.connect(host="localhost" ,  database="fastapi", user="postgres", password='5432' , cursor_factory=RealDictCursor)
        cursor=conn.cursor()
        print("Data-base connected succesfully..")
        break
    except Exception as error:
        print("Data-base cconnection faild",error)
        time.sleep(3)

app = FastAPI()   # u can mention any app name


@app.get("/",response_class=HTMLResponse)               # @ --> refers the entry point of back end;
def read_root(request:Request):
    return templates.TemplateResponse("landpage.html",{"request":request})

@app.get("/landpage.html", response_class=HTMLResponse)
def landpage(request: Request):
    return templates.TemplateResponse("landpage.html", {"request": request})


@app.get("/form.html", response_class=HTMLResponse)
def show_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/form.html", response_class=HTMLResponse)
def create_post(request: Request, title: str = Form(...), content: str = Form(...)):
    cursor.execute("INSERT INTO spost(title, content) VALUES(%s, %s)", (title, content))
    conn.commit()
    return RedirectResponse(url="/landpage.html", status_code=303)



@app.get("/displaypost.html",response_class=HTMLResponse)          # if in wesite is looks like: http://127.0.0.1:8000/posts
def read_post(request:Request):
    cursor.execute("SELECT * FROM spost")
    records = cursor.fetchall()
    return templates.TemplateResponse("displaypost.html",{"request":request,"posts":records})    # returning the data to front end...




@app.get("/deletepost.html/{id}", response_class=HTMLResponse)
def delete_post(request: Request, id: int):
    cursor.execute("DELETE FROM spost WHERE id = %s", (id,))
    conn.commit()
    return RedirectResponse(url="/displaypost.html", status_code=303)

#-------update  handling-------------


#@app.get("/updatepage.html", response_class=HTMLResponse)
#def show_update_form(request: Request):
    #id =request.query_params.get("id")
    #con =request.query_params.get("content")
   # return f"<h3>✅ Post with ID {id} deleted.</h3><a href='/'>Back to Home</a>"



@app.get("/updatepage.html", response_class=HTMLResponse)
async def load_update_page(request: Request):
    id = request.query_params.get("id")
    content = request.query_params.get("content")

    if not id or not content:
        return HTMLResponse(content="❌ Invalid access. ID or Content missing.", status_code=400)

    return templates.TemplateResponse("updatepage.html", {
        "request": request,
        "id": id,
        "content": content
    })



from fastapi import Form
from fastapi.responses import RedirectResponse

@app.post("/updatepage.html")
async def update_post(id: str = Form(...), content: str = Form(...)):
    cursor.execute("UPDATE spost SET content = %s WHERE id = %s", (content, id))
    conn.commit()
    return RedirectResponse(url="/displaypost.html", status_code=303)
