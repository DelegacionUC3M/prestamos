package routes

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"time"
)

var (
	noDataError = ""
)

// LoginPage asks the user for their credentials
//
// If the user is authenticated correctly, redirects to the main page
func LoginPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")

	t, _ := template.ParseFiles("./templates/index.html")

	switch r.Method {
	case http.MethodPost:
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
		body, err := ioutil.ReadFile("./templates/login.html")
		if err != nil {
			panic(err)
		}
		fmt.Fprintf(w, string(body))

		// t.Execute(w, "")
	}
}

// IndexPage is the main page for the application
//
// Shows a preview of the loans and objects
func IndexPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	if r.Method == http.MethodPost {
		r.ParseForm()
		name := r.FormValue("nia")
		t, _ := template.ParseFiles("./templates/index.html", "./templates/navbar.html")

		t.Execute(w, name)
	} else {

		cookie, err := r.Cookie("role")
		if err != nil {
			panic(err)
		}

		t, _ := template.ParseFiles("./templates/index.html", "./templates/navbar.html")
		t.Execute(w, cookie.Value)
	}
}
