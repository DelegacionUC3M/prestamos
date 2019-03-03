package private

import (
	"fmt"

	"github.com/BurntSushi/toml"
)

// Database holds the members to initialse the db connection
type Database struct {
	Name     string
	User     string
	Password string
}

type Databases struct {
	Loans Database
	Users Database
}

// ParseConfig parses the config for the database
func ParseConfig(file string) (Databases, error) {

	var tomlConfig Databases
	_, err := toml.DecodeFile(file, &tomlConfig)

	return tomlConfig, err
}

// CreateDbInfo formats the data to create a connection to the database
func CreateDbInfo(config Database) string {
	connection := fmt.Sprintf("user=%s password=%s dbname=%s sslmode=disable", config.User, config.Password, config.Name)

	return connection
}
