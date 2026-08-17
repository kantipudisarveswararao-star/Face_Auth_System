from database import init_db
from gui_app import FaceAuthApp

def main():
    init_db()
    app = FaceAuthApp()
    app.mainloop()

if __name__ == "__main__":
    main()