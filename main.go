package main

import (
	"fmt"
	"net/http"
	"time"

	"github.com/gorilla/mux"

	"github.com/jinzhu/gorm"
	_ "github.com/lib/pq"

	models "github.com/DelegacionUC3M/prestamos/models"
	private "github.com/DelegacionUC3M/prestamos/private"
	routes "github.com/DelegacionUC3M/prestamos/routes"
)

// Defualt configuration options
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
	// TODO: Change fmt to log
	fmt.Println("Database connection established")

	Routes := new(routes.RouteStruct)
	Routes.DB = db
	
	// Create the database schema
	db.AutoMigrate(&models.Item{}, &models.Loan{}, &models.Penalty{})

	// itemOne := models.Item{Name:"Test", Amount:0, Type:"Testing", State:"Func", LoanDays:5, PenaltyCoefficient: 4}
	// itemTwo := models.Item{Name:"Objeto", Amount:5, Type:"Lab", State:"Roto", LoanDays:3, PenaltyCoefficient: 2}
	
	// db.Create(&itemOne)
	// db.Create(&itemTwo)

	r := mux.NewRouter().StrictSlash(true)
	srv := &http.Server{
		Addr:         "0.0.0.0" + defaultPort,
		WriteTimeout: time.Second * 15,
		ReadTimeout:  time.Second * 15,
		IdleTimeout:  time.Second * 60,
		Handler:      r,
	}

	r.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))
	
	r.HandleFunc("/login", Routes.LoginPage).Methods("GET", "POST")
	r.HandleFunc("/index", Routes.IndexPage).Methods("GET", "POST")

	r.HandleFunc("/item/create", Routes.ItemCreate).Methods("GET", "POST")
	
	r.HandleFunc("/loan/create", Routes.LoanCreate).Methods("GET", "POST")

	
	fmt.Printf("App listening on port %s\n", defaultPort)
	if err = srv.ListenAndServe(); err != nil {
		panic(err)
	}
}
