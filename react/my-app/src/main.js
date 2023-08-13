import { Component } from "react";
import RecordVideo from "./WebcamVideo";
import RecorVoice from "./RecordVoice";
import Nav from "./nav";
export default class Main extends Component {
    constructor(props){
      super(props)
      this.state = {
        isActiveGuests: false,
        isActiveVoice: false
      }
      this.showPage = this.showPage.bind(this)
    }

    showPage(evt){
        let dest = evt.target.classList[0]
        if(dest === 'nav-arrow-left'){
            document.querySelector('.Container').classList.remove('hidden')
            this.setState((state) => ({isActiveGuests: true}))
        }
        else{
            this.setState((state) => ({isActiveVoice: true}))
        }
    }
    

    render() {
        console.log(this.props)
        return (
            <div>
                <RecordVideo AddHistory={this.props.AddHistory}/>
                <RecorVoice isActive={this.state.isActiveVoice}/>
                <div className="main-nav">
                    <Nav ShowPage={this.showPage} isActive={!this.state.isActiveGuests && !this.state.isActiveVoice}/>
                </div>
            </div>
    )}
}