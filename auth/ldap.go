package auth

import (
	"fmt"

	"database/sql"

	_ "github.com/lib/pq"

	"github.com/mqu/openldap"

	"github.com/DelegacionUC3M/prestamos/private"
)

const (
	ldapServer = "ldaps://ldap.uc3m.es"
	baseDN     = "ou=Gente,o=Universidad Carlos III,c=es"
	RolUser    = 10
	RolAdmin   = 50
	RolManager = 100
)

// UserData holds basic info from a ldap query
type UserData struct {
	Name string
	NIA  int
	Card int
}

// CheckCredentials authenticates a student from the university
func CheckCredentials(name string, pass string) bool {
	ldap, err := openldap.Initialize(ldapServer)
	if err != nil {
		panic(err)
	}
	defer ldap.Close()

	ldap.SetOption(openldap.LDAP_OPT_PROTOCOL_VERSION, openldap.LDAP_VERSION3)

	// If we get an error, the credentials are not valid
	if err = ldap.Bind(name, pass); err != nil {
		return false
	}

	return true
}

// GetUserData retrieves UserData from a certain user
func GetUserData() (UserData, error) {
	ldap, err := openldap.Initialize(ldapServer)
	if err != nil {
		panic(err)
	}
	defer ldap.Close()

	ldap.SetOption(openldap.LDAP_OPT_PROTOCOL_VERSION, openldap.LDAP_VERSION3)
	scope := openldap.LDAP_SCOPE_SUBTREE

	filter := "cn=*admin*"

	_, err = ldap.Search(baseDN, scope, filter, []string{})
	if err != nil {
		return UserData{}, err
	}

	// TODO: Get the data out of the ldap query
	var data UserData
	// data.Name = result.
	// data.NIA =
	// data.Card =

	return data, nil
}

// CheckUserRol provides the rol of a certain user
func CheckUserRol(nia string) int {

	privateConfig, err := private.ParseConfig("./config.toml")
	if err != nil {
		panic(err)
	}

	dbUsersConn := private.CreateDbInfo(privateConfig.Users)
	db, err := sql.Open("postgres", dbUsersConn)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	query := fmt.Sprintf("SELECT role FROM privilege WHERE id_person = (SELECT id_person FROM person WHERE nia=%s)", nia)

	row, err := db.Query(query)
	if err != nil {
		panic(err)
	}

	var privilege int
	row.Scan(&privilege)

	// TODO: Check what happens if the user is not found
	return privilege
}
