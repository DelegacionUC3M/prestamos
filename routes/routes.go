package routes

import (
	"fmt"
	"log"
	"os"
	// "html/template"
	"io/ioutil"
	"strconv"
	"net/http"
	"time"

	"github.com/jinzhu/gorm"
	_ "github.com/lib/pq"

	models "github.com/DelegacionUC3M/prestamos/models"	
)

// Default options for the logger
var (
	logger  = createLogger()
	logFile = "./prestamos.log"
)

var (
	loc, _ = time.LoadLocation("Europe/Madrid")
)

// RouteStruct allows us to pass the db handle without problem
// We only need to instantiate one object since all routes can be accessed as methods
type RouteStruct struct {
	DB *gorm.DB
}

// IndexInfo contains information to display on the index page
type IndexInfo struct {
	Items []models.Item
	Loans []models.Loan
	Modal string // Info to show on the modal
}

// NewIndexInfo creates a new IndexInfo object
func NewIndexInfo() IndexInfo {
	return IndexInfo{ make([]models.Item,1), make([]models.Loan,1), ""}
}

// GatherIndexInfo querys items and loans for the index page
// The Modal field is unchanged
func (R *RouteStruct) GatherIndexInfo(info *IndexInfo) {

	var (
		itemholder models.Item
		loanholder models.Loan
	)

	itemsRows, err := R.DB.Model(&models.Item{}).Where("amount = 0").Rows()
	if err != nil {
		panic(err)
	}
	defer itemsRows.Close()

	for itemsRows.Next() {
		R.DB.ScanRows(itemsRows, &itemholder)
		info.Items = append(info.Items, itemholder)
	}
	
	loansRows, err := R.DB.Model(&models.Loan{}).Where("finished = ?", "false").Rows()
	if err != nil {
		panic(err)
	}
	defer loansRows.Close()

	for loansRows.Next() {
		R.DB.ScanRows(loansRows, &loanholder)
		// FIXME: Parsing between different formats
		// loanholder.LoanDate, _ = time.ParseInLocation("01-02-2006 15:04:05", loanholder.LoanDate.String(), loc)
		// loanholder.RefundDate, _ = time.ParseInLocation("01-02-2006 15:04:05", loanholder.RefundDate.String(), loc)

		info.Loans = append(info.Loans, loanholder)
	}
}

// Creates a Logger to log all http requests onto the logFile
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
// Else, show the error and stay in the page
func (R *RouteStruct) LoginPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html; charset=utf-8")

	if r.Method == http.MethodPost {
		logger.Printf("POST %s %s", r.URL, r.RemoteAddr)
		// TODO: Obtain the user role from the db
		// TODO: Obtain if user is valid using ldap
		r.ParseForm()
		name := r.FormValue("nia")

		// The cookie allows us to check if the user is authenticated
		// It will expire after 1 hour to prevent unauthorized access
		expire := time.Now().AddDate(0, 0, 1)
		cookie := http.Cookie{
			Name:    "role",
			Value:   name,
			Expires: expire,
		}
		http.SetCookie(w, &cookie)
		TIndex.Execute(w, name)

	} else {
		logger.Printf("GET %s", r.URL)
		TLogin.Execute(w, "")
	}
}

// IndexPage is the main page for the application
//
// Shows a preview of the loans which are yet to be refunded and objects out of stock
func (R *RouteStruct) IndexPage(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	indexInfo := NewIndexInfo()
	
	if r.Method == http.MethodPost {
		logger.Printf("POST %s %s", r.URL, r.RemoteAddr)
		// r.ParseForm()
		// nia := r.FormValue("nia")
		// TIndex.Execute(w, nia)
		R.GatherIndexInfo(&indexInfo)
		TIndex.Execute(w, indexInfo)
		
	} else {
		logger.Printf("GET %s %s", r.URL, r.RemoteAddr)
		R.GatherIndexInfo(&indexInfo)
		TIndex.Execute(w, indexInfo)
	}
}

// ItemCreate shows a form to create an item and insert it into the database
func (R *RouteStruct) ItemCreate(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")

	indexInfo := NewIndexInfo()

	var itemholder models.Item
	
	if r.Method == http.MethodPost {
		logger.Printf("POST %s %s", r.URL, r.RemoteAddr)
		r.ParseForm()
		itemholder.Name = r.FormValue("name")
		itemholder.Amount, _ = strconv.Atoi(r.FormValue("amount"))
		itemholder.Type = r.FormValue("type")
		itemholder.State = r.FormValue("state")
		itemholder.LoanDays, _ = strconv.Atoi(r.FormValue("loan_days"))
		coeff, _ := strconv.ParseFloat(r.FormValue("penalty_coefficient"), 64)
		itemholder.PenaltyCoefficient = coeff

		R.DB.Create(&itemholder)
		R.GatherIndexInfo(&indexInfo)
		TIndex.Execute(w, indexInfo)
		
	} else {
		logger.Printf("GET %s %s", r.URL, r.RemoteAddr)
		TItemCreate.Execute(w, "")
	}
}

func (R *RouteStruct) LoanCreate(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	
	var loanholder models.Loan
	
	if r.Method == http.MethodPost {
		logger.Printf("POST %s %s", r.URL, r.RemoteAddr)
		r.ParseForm()
		loanholder.ItemID, _ = strconv.Atoi(r.FormValue("objeto"))
		loanholder.Nia, _ = strconv.Atoi(r.FormValue("user"))
		loanholder.Amount, _ = strconv.Atoi(r.FormValue("amount"))
		t, _ := time.ParseInLocation("01-02-2006", r.FormValue("loan_date"), loc)
		loanholder.LoanDate = t
		R.DB.Create(&loanholder)

		indexInfo := NewIndexInfo()
		R.GatherIndexInfo(&indexInfo)
		TIndex.Execute(w, indexInfo)
		
	} else {
		logger.Printf("GET %s %s", r.URL, r.RemoteAddr)

		var (
			itemholder models.Item
			itemlist []models.Item
		)
		
		itemsRows, err := R.DB.Model(&models.Item{}).Rows()
		if err != nil {
			panic(err)
		}
		defer itemsRows.Close()

		for itemsRows.Next() {
			R.DB.ScanRows(itemsRows, &itemholder)
			itemlist = append(itemlist, itemholder)
		}
		TLoanCreate.Execute(w, itemlist)
	}

}
