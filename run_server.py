import app

if __name__ == "__main__":
    # Start Flask app without debug/reloader
    app.app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
