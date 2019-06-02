package routes

import (
	"fmt"
	"log"
	"os"
	"html/template"
	"io/ioutil"
	"net/http"
	"time"
)

var (
	noDataError = ""
)

var (
	logger = createLogger()
	logFile     = "./prestamos.log"
)

func createLogger() *log.Logger {
	lf, err := os.OpenFile(logFile, os.O_WRONLY|os.O_CREATE|os.O_APPEND, 0640)
	if err != nil {
		log.Fatal("No se pudo abrir el archivo de log:", err)
	}
	return log.New(lf, "[Prestamos] ", log.LstdFlags)	
}

// TODO: Use the error into the template
func returnToLogin(w http.ResponseWriter) {
	body, err := ioutil.ReadFile("./templates/login.html")
	if err != nil {
		panic(err)
	}
	fmt.Fprintf(w, string(body))
}
// LoginPage asks the user for their credentials
//
// If the user is authenticated correctly, redirects to the main page
func LoginPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")

	t, _ := template.ParseFiles("./templates/index.html")

	switch r.Method {
	case http.MethodPost:
		logger.Printf("POST %s", r.URL)
		// TODO: Obtain the user role from the db
		r.ParseForm()
		name := r.FormValue("nia")

		// if err := auth.CheckUserRol(name); err != nil {
		//     error = ...
		//     t.Execute(w, error)
		// }

		expire := time.Now().AddDate(0, 0, 1)
		cookie := http.Cookie{
			Name:    "role",
			Value:   name,
			Expires: expire,
		}
		http.SetCookie(w, &cookie)

		t.Execute(w, name)

	case http.MethodGet:
		logger.Printf("GET %s", r.URL)
		returnToLogin(w)
	}
}

// IndexPage is the main page for the application
//
// Shows a preview of the loans and objects
func IndexPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	if r.Method == http.MethodPost {
		logger.Printf("POST %s", r.URL)
		r.ParseForm()
		nia := r.FormValue("nia")
		t, _ := template.ParseFiles("./templates/index.html", "./templates/navbar.html")

		t.Execute(w, nia)
	} else {
		logger.Printf("GET %s", r.URL)
		cookie, err := r.Cookie("role")
		if err != nil {
			returnToLogin(w)
		}

		t, _ := template.ParseFiles("./templates/index.html", "./templates/navbar.html")
		t.Execute(w, cookie.Value)
	}
}
