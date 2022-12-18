import { FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material'
import React from 'react'

export const ByDate = ({state, setState, dates}) => {
 
  return (
    <FormControl fullWidth>
    <InputLabel id="demo-simple-select-label">Date</InputLabel>
    <Select
      labelId="demo-simple-select-label"
      id="demo-simple-select"
      value={state || ""}
      label="Date"
      onChange={(e) => {setState(e.target.value)}}
    >
      {
        dates?.map((ele, i) => (
          <MenuItem key={i} value={ele}>{ele}</MenuItem>
        ))
      }
    </Select>
  </FormControl>
  )
}
