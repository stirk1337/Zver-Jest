import { Component } from "react";
import { HashRouter, Routes, Route, NavLink } from "react-router-dom";
import './App.css';

export default class Nav extends Component {
  constructor(props){
    super(props)
    this.state = {

    }
  }

  render() {
    console.log(this.props.isActive)
    if(this.props.isActive){
        return (
            <div>
                <p className="guest-translate">Переведи жесты</p>
                <p className="in-word">в слова</p>
                <img className="nav-arrow-left" src="arrow-left.svg" alt="лево" onClick={this.props.ShowPage}></img>
                <img className="nav-arrow-right" onClick={this.props.ShowPage} src="arrow-right.svg" alt="право"></img>
            </div>
        )
    }
  }
}