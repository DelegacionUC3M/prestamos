package main

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"

	"github.com/jinzhu/gorm"
	_ "github.com/lib/pq"

	// models "github.com/DelegacionUC3M/prestamos/models"
	private "github.com/DelegacionUC3M/prestamos/private"
	routes "github.com/DelegacionUC3M/prestamos/routes"
)

const (
	defaultPort = ":8000"
	tomlFile    = "./config.toml"
)

func main() {

	privateConfig, err := private.ParseConfig(tomlFile)
	if err != nil {
		panic(err)
	}

	dbLoansConn := private.CreateDbInfo(privateConfig.Loans)

	db, err := gorm.Open("postgres", dbLoansConn)
	if err != nil {
		panic(err)
	}
	defer db.Close()
	fmt.Println("Database connection established")

	r := mux.NewRouter().StrictSlash(true)
	r = r.PathPrefix("/prestamos").Subrouter()

	srv := &http.Server{
		Addr:         "0.0.0.0" + defaultPort,
		WriteTimeout: time.Second * 15,
		ReadTimeout:  time.Second * 15,
		IdleTimeout:  time.Second * 60,
		Handler:      r,
	}

	r.Handle("/static", http.FileServer(http.Dir("./static/")))
	r.HandleFunc("/login", routes.LoginPage).Methods("GET", "POST")
	r.HandleFunc("/index", routes.IndexPage).Methods("GET", "POST")

	fmt.Printf("App listening on port %s\n", defaultPort)
	if err = srv.ListenAndServe(); err != nil {
		panic(err)
	}
}
