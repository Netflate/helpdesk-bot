package repositories

import (
	"context"
	"site/internal/models"

	"github.com/jackc/pgx/v5/pgxpool"
)

type EmployeeRepository struct {
	db *pgxpool.Pool
}

func NewEmployeeRepository(db *pgxpool.Pool) *EmployeeRepository {
	return &EmployeeRepository{db}
}

func (r *EmployeeRepository) GetAll(ctx context.Context) ([]models.Employee, error) {
	rows, err := r.db.Query(ctx, "SELECT ID, NAME, STATUS, ROLE FROM EMPLOYEES")
	if err != nil {
		return nil, err
	}

	defer rows.Close()

	var list []models.Employee
	for rows.Next() {
		var e models.Employee
		if err := rows.Scan(&e.ID, &e.Name, &e.Status, &e.Role); err != nil {
			return nil, err
		}
		list = append(list, e)
	}

	return list, nil
}
