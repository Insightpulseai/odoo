variable "zone_id" {
  type = string
}

variable "zone_name" {
  type = string
}

variable "origin_ipv4" {
  type = string
}

variable "zoho_mx" {
  type = list(object({
    priority = number
    host     = string
  }))
}

variable "app_subdomains" {
  type = list(string)
}

variable "extra_a_subdomains" {
  type    = list(string)
  default = []
}

variable "txt_records" {
  type    = map(list(string))
  default = {}
}

variable "dkim" {
  type = object({
    enabled  = bool
    selector = string
    value    = string
  })
  default = {
    enabled  = false
    selector = "zoho"
    value    = "TODO"
  }
}
