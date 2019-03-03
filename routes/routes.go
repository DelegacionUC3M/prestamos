package routes

import (
	"fmt"
	"html/template"
	"io/ioutil"
	"net/http"
	"time"
)

// From the go wiki https://golang.org/doc/articles/wiki/
// func loadPage(title string) (*Page, error) {
//     filename := title + ".txt"
//     body, err := ioutil.ReadFile(filename)
//     if err != nil {
//         return nil, err
//     }
//     return &Page{Title: title, Body: body}, nil
// }
// And then in a handler function
//     p, err := loadPage(title)
//     t, _ := template.ParseFiles("edit.html")
//     t.Execute(w, p)

// LoginPage asks the user for their credentials
//
// If the user is authenticated correctly, redirects to the main page
func LoginPage(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		// TODO: Obtain the user role from the db
		r.ParseForm()
		name := r.FormValue("nia")
		// t, _ := template.ParseFiles("./templates/index.html")
		expire := time.Now().AddDate(0, 0, 1)
		cookie := http.Cookie{
			Name:    "role",
			Value:   name,
			Expires: expire,
		}
		http.SetCookie(w, &cookie)
		http.Redirect(w, r, "/index", http.StatusSeeOther)
	} else {

		body, err := ioutil.ReadFile("./templates/login.html")
		if err != nil {
			panic(err)
		}

		fmt.Fprintf(w, string(body))
	}

}

// IndexPage is the main page for the application
//
// Shows a preview of the loans and objects
func IndexPage(w http.ResponseWriter, r *http.Request) {
	if r.Method == http.MethodPost {
		r.ParseForm()
		name := r.FormValue("nia")
		t, _ := template.ParseFiles("./templates/index.html")
		t.Execute(w, name)
	} else {

		cookie, err := r.Cookie("role")
		if err != nil {
			panic(err)
		}

		t, _ := template.ParseFiles("./templates/index.html")
		t.Execute(w, cookie.Value)
		// fmt.Fprint(w, fmt.Sprintf("<h1>Hello %s</h1>"))
	}
}
