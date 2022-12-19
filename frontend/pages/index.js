import dynamic from 'next/dynamic';

const VectorMap = dynamic(
  // @ts-ignore
  () => import("@react-jvectormap/core").then((m) => m.VectorMap),
  { ssr: false, }
);

import rmMill from "../Comunas/rmclMill.json";
import Container from '@mui/material/Container'
import Grid from '@mui/material/Grid';
import { flexbox } from '@mui/system';
import { Box, Breadcrumbs, Button, LinearProgress, Link, Typography } from '@mui/material';
import { useEffect, useState } from 'react';
import { ByDate } from '../components/ByDate';
import { Prueba } from '../components/Prueba';
import BarCharts from '../components/BarCharts';
const axios = require('axios');

const mapDataa = {
  "Padre Hurtado":1,
"Maipú":2,
"Cerrillos":3,
"Estación Central":4,
"Pudahuel":5,
"Lo Prado ":6,
"Cerro Navia":7,
"Santiago":2,
"Renca":20,
"Quinta Normal":20,
"Recoleta":20,
"Independencia":20,
"Quilicura":20,
"Conchalí":20,
"San Bernardo":20,
"El Bosque":20,
"La Cisterna": 20,
"Lo Espejo":20,
"Pedro Aguirre Cerda":20,
"San Miguel":20,
"San Ramón":20,
"La Granja":20,
"San Joaquín":20,
"La Pintana":20,
"Providencia":20,
"Ñuñoa":20,
"La Reina":20,
"Macul":20,
"Puente Alto":20,
"Pirque":20,
"San José de Maipo":20,
"La Florida":20,
"Peñalolén":20,
"Las Condes":20,
"Vitacura":20,
"Lo Barnechea":20,
"Huechuraba":20,

}






export default function Home() {

  let mapdata = {}
  const [date, setDate] = useState(null);
  const [spinner, setSpinner] = useState(false);
  const [showGraph, setShowGraph ] = useState(true);
  const [dataFromDay, setDataFromDay] = useState(null);
  const [dates, setDates] = useState([]);
  const [showDate, setShowDate] = useState(false)
  const [showComune, setShowComune] = useState(false);
  const [comune, setComune] = useState(false)
  const [fetchComune, setFetchComune] = useState(false);
  const [dataBarcharts, setDataBarcharts] = useState([]);
  useEffect(() => {
    axios.get('http://localhost:5000/predictdates')
  .then(function (response) {
     setDates(response.data)
     setShowDate(true)
  })
  .catch(function (error) {
    console.log(error);
  })

  axios.get('http://localhost:5000/comunas')
  .then((res) => {
    console.log(res.data)
    setShowComune(true)
    res.data.forEach((ele,i) => {
      const first = ele.charAt(0).toUpperCase()
      const rest = ele.slice(1)
      res.data[i] = first + rest
    })
    setFetchComune(res.data)
  })
  .catch((err)=> {
    console.log(err)
  })
  }, [])


   const regionStyle = {
    initial: {
      fill: "#e4e4e4",
      "fill-opacity": 0.9,
      stroke: "none",
      "stroke-width": 0,
      "stroke-opacity": 0
    },
    hover: {
      "fill": "#763452",
      "fill-opacity": 0.9,
    }
  };
  
  const containerStyle = {
    width: "inherited",
    height: "inherited",  
  };

  const series = {
    regions: [{
      values: dataFromDay,
      scale: ["#e4e4e4", "#763452"],
      normalizeFunction: "polynomial"
    },]
  }


  const dataToRender = (val) => {
    setShowGraph(val);
  }

  const sendDataGeo = async (e) => {
    e.preventDefault();
    setSpinner(true);
    axios.get(`http://localhost:5000/datafromday?fecha=${date}`)
  .then(function (response) {
    setSpinner(false);

    let dataFinal = {}
    let min = Number.MAX_VALUE
     response.data.forEach(ele => {
      let value = ele[Object.keys(ele)[0]]
      
      if(value < min){
        min = value
      }
      //console.log(value)
      let arrayOfWord = Object.keys(ele)[0].split(" ")
      arrayOfWord.forEach((word,i) =>{
        const firstUpLetter = word.charAt(0).toUpperCase()
        const restOfWord = word.slice(1)
        arrayOfWord[i] = firstUpLetter + restOfWord
        
      })
      dataFinal[arrayOfWord.join(" ")] = value
    })
    Object.keys(dataFinal).forEach(ele => {
      dataFinal[ele] = dataFinal[ele] + (min * -1)
    })
    setDataFromDay(dataFinal)
  })
  .catch(function (error) {
    setSpinner(false);
    console.log(error);
  })

  }

  const sendDataLine = async(e)=> {
    e.preventDefault();
    setSpinner(true);
    axios.get(`http://localhost:5000/alldata?comuna=${comune}`)
    .then(function (response) {
      console.log(response)
      setSpinner(false);
      let dataFinal = [];
      let min = Number.MIN_VALUE;
      Object.keys(response.data).forEach(ele => {
        const obj = {date: ele, value: response.data[ele]}
        dataFinal.push(obj);
        if(obj.value < min){
          min = obj.value
        }
      })
      dataFinal.forEach(ele => {
        ele.value = ele.value + (min * -1)
      })
      setDataBarcharts(dataFinal)
    })
    .catch((err) => {
      console.log(err)
    })
  }

  return (
    <Container >
      <Grid container spacing={2} >
        <Grid sx={{display: "flex", alignItems: "center", mt:5}} item xs={12} xl={12} md={12} lg={12} >
         {
          (spinner) ? (<Box sx={{ width: '100%' }}>
          <LinearProgress />
        </Box>) : ( <Box sx={{display: "flex", flexDirection: "column"}}>

              <div role="presentation" >
              <Breadcrumbs sx={{mb: 3}} aria-label="breadcrumb">
                <Button  underline="hover" color="inherit" onClick={() => dataToRender(true)} >
                  Geographical
                </Button>
                <Button  underline="hover" color="inherit" onClick={() => dataToRender(false)} >
                  Line graph
                </Button>
              </Breadcrumbs>
              </div>
        
        
            
              {(showGraph) ? ( <div style={{width: "1000px", height: "600px",}}>
              <VectorMap
                map={rmMill}
                backgroundColor="transparent"
                zoomOnScroll={false}
                containerStyle={containerStyle}
                containerClassName="map"
                regionStyle={regionStyle}
                series={series}
              />
              </div>) : (<BarCharts data={dataBarcharts}/>)}
            
            
            </Box>)
         }
        </Grid>
        <Grid  sx={{mt:5}} item xs={12} xl={12} md={12} lg={12}>
          
        
          { 
          
            (showGraph) ? (showDate && <ByDate state={date} setState={setDate} dates={dates} label="Date"/>)
            : (showComune && <ByDate state={comune} setState={setComune} dates={fetchComune} label="Comune"/>)
          
          
          }
          <div style={{height: "3rem",display: "flex", justifyContent: "end", mt:5}}>
            <Button sx={{mt:4, p: 2}} variant="contained"  onClick={(showGraph) ? sendDataGeo : sendDataLine}>refresh</Button>
          </div>
           
        </Grid>
      </Grid>
    
    </Container>
  )
}
