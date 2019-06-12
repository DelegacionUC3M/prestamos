package models

import (
	"time"
	"github.com/jinzhu/gorm"
)

// Item stores the information from a lendable object
type Item struct {
	// ID                 uint    `gorm:"primary_key";"AUTO_INCREMENT"`
	gorm.Model
	Name               string  `gorm:"not_null"`
	Amount             int	   `gorm:"not_null"`
	Type               string  `gorm:"not_null"`
	State              string  `gorm:"not_null"`
	LoanDays           int	   `gorm:"not_null"`
	PenaltyCoefficient float64 `gorm:"not_null"`
}

// Loan stores a loan made from a user
type Loan struct {
	// ID         uint `gorm:"primary_key";"AUTO_INCREMENT"`
	gorm.Model
	Item       Item `gorm:"foreignkey:ItemID"`
	ItemID     int 
	Nia        int  `gorm:"not null"`
	Amount     int
	LoanDate   time.Time
	RefundDate time.Time
	Finished   bool `gorm:"default:false"`
}

// Penalty stores a sanction from a user
type Penalty struct {
	// ID           uint `gorm:"primary_key";"AUTO_INCREMENT"`
	gorm.Model
	Nia          int
	Loan         Loan `gorm:"foreignkey:LoanID"`
	LoanID       int
	SanctionDate time.Time
	PenaltyDate  time.Time
}
