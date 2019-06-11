package routes

import (
	"html/template"
)

// Templates for all the routes 
var (
	navbar = "./templates/navbar.html"
	modal  = "./templates/modal.html"
	TLogin, _ = template.ParseFiles("./templates/login.html", navbar, modal)
	TIndex, _ = template.ParseFiles("./templates/index.html", navbar, modal)

	// Item templates
	TItemList, _   = template.ParseFiles("./templates/item_list.html", navbar, modal)
	TItemCreate, _ = template.ParseFiles("./templates/item_create.html", navbar, modal)
	TItemEdit, _   = template.ParseFiles("./templates/item_edit.html", navbar, modal)	
	TItemDelete, _ = template.ParseFiles("./templates/item_delete.html", navbar, modal)

	// Loan templates
	TLoanList, _   = template.ParseFiles("./templates/loan_list.html", navbar, modal)
	TLoanCreate, _ = template.ParseFiles("./templates/loan_create.html", navbar, modal)
	TLoanDelete, _ = template.ParseFiles("./templates/loan_delete.html", navbar, modal)
	TLoanEdit, _   = template.ParseFiles("./templates/loan_edit.html", navbar, modal)

	// Penalties templates
	TPenaltyList, _   = template.ParseFiles("./templates/petalty_list.html", navbar, modal)
	TPenaltyCreate, _ = template.ParseFiles("./templates/penalty_create.html", navbar, modal)
	TPenaltyDelete, _ = template.ParseFiles("./templates/penalty_delete.html", navbar, modal)
	TPenaltyEdit, _   = template.ParseFiles("./templates/penalty_edit.html", navbar, modal)
)

// Diferent errors to return with the templates
var (
	// No data was given in the form
	NoDataError = ""
	// Maximum number of loan
	MaxLoansError = ""
	// The user has a penalty
	UserPenaltyError = ""
)
