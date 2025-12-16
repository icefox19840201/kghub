import uvicorn
import root_urls
import dotenv
dotenv.load_dotenv()
app=root_urls.app
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
