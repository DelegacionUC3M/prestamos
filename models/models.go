package models

import (
	"time"
)

// Item stores the information from a lendable object
type Item struct {
	ID                 uint `gorm:"primary_key" gorm:"AUTO_INCREMENT"`
	Name               string
	Amount             int
	Type               string
	State              string
	LoanDays           int
	PenaltyCoefficient float32
}

// Loan stores a loan made from a user
type Loan struct {
	ID         uint `gorm:"primary_key" gorm:"AUTO_INCREMENT"`
	ItemID     int
	Item       Item
	Nia        int
	Amount     int
	LoanDate   time.Time
	RefundDate time.Time
}

// Penalty stores a sanction from a user
type Penalty struct {
	ID           uint `gorm:"primary_key" gorm:"AUTO_INCREMENT"`
	Nia          int
	Loan         Loan `gorm:"foreignkey:LoanID"`
	LoanID       int
	SanctionDate time.Time
	PenaltyDate  time.Time
}
