import { Component } from "react";
import { HashRouter, Routes, Route, NavLink } from "react-router-dom";
import './App.css';
import Main from "./main";
import HeaderIcons from "./HeaderIcons";
import History from "./History";

export default class App extends Component {
  constructor(props){
    super(props)
    this.state = {
      history: [],
      saved: []
    }
    this.AddHistory = this.AddHistory.bind(this)
  }

  AddHistory(newHistoryData){
    console.log(newHistoryData)
    let arr = [...this.state.history]
    arr.push(newHistoryData)
    this.setState({history: arr})
  }

  render() {
    return (
        <div>
          <header>
            <img className="header-back" src="header.svg" alt="Шапка"></img>
            <img src="logo.svg" alt="Лого"></img>
            <div className="icons">
              <HeaderIcons name={'Сохранённые'} color={'black'}/>
              <HeaderIcons name={'История'} color={'black'}/>
              <HeaderIcons name={'Голос'} color={'black'}/>
            </div>
          </header>
          <img className="ekb-icon" src="ekb300logo.svg" alt="Лого"></img>
          <History History={this.state.history}/>
          <Main AddHistory={this.AddHistory}/>
          <div className="footer">
            <img src="footer.svg" alt="подвал"></img>
          </div>
        </div>
    )
  }
}