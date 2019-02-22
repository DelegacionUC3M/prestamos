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

// ParseConfig parses the config for the database
func ParseConfig(file string) (Database, error) {

	var tomlConfig Database
	_, err := toml.DecodeFile(file, &tomlConfig)

	return tomlConfig, err
}

// CreateDbInfo formats the data to create a connection to the database
func CreateDbInfo(config Database) string {
	connection := fmt.Sprintf("user=%s password=%s dbname=%s sslmode=disable", config.User, config.Password, config.Name)

	return connection
}
