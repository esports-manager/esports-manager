import webview

if __name__ == "__main__":
    window = webview.create_window(
        "eSports Manager", url="http://localhost:5173/", resizable=True
    )
    webview.start()
