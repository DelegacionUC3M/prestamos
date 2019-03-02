package routes

import (
	"fmt"
	"net/http"
)

// LoginPage asks the user for their credentials
//
// If the user is authenticated correctly, redirects to the main page
func LoginPage(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "<h1>Login page</h1>")
}
