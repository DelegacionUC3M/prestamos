package main

import (
	"fmt"

	"github.com/jinzhu/gorm"
	_ "github.com/lib/pq"

	// models "github.com/DelegacionUC3M/prestamos/models"
	private "github.com/DelegacionUC3M/prestamos/private"
)

func main() {

	privateConfig, err := private.ParseConfig("./config.toml")
	if err != nil {
		panic(err)
	}

	dbconn := private.CreateDbInfo(privateConfig)

	db, err := gorm.Open("postgres", dbconn)
	if err != nil {
		panic(err)
	}
	fmt.Printf("Database connection established")

	db.Close()
}
