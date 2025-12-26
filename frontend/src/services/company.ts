import api from './api'

export interface CreateCompanyData {
  name: string
  legal_name?: string
  tax_id?: string
  address_line1?: string
  address_line2?: string
  city?: string
  state?: string
  postal_code?: string
  country?: string
  phone?: string
  website?: string
}

export interface Company {
  id: number
  name: string
  slug: string
  database_name: string | null
}

export const companyService = {
  async createCompany(data: CreateCompanyData): Promise<Company> {
    const response = await api.post<Company>('/api/company', data)
    return response.data
  }
}

