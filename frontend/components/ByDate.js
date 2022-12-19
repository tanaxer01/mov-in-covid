import { FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material'
import React from 'react'

export const ByDate = ({state, setState, dates, label}) => {
 
  return (
    <FormControl fullWidth>
    <InputLabel id="demo-simple-select-label">{label}</InputLabel>
    <Select
      labelId="demo-simple-select-label"
      id="demo-simple-select"
      value={state || ""}
      label={label}
      onChange={(e) => {setState(e.target.value)}}
    >
      {
        dates?.map((ele, i) => (
          <MenuItem key={i} value={ele.toLowerCase()}>{ele}</MenuItem>
        ))
      }
    </Select>
  </FormControl>
  )
}
