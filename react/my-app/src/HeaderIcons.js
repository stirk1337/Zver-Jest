import { Component } from "react";
export default class HeaderIcons extends Component {
    constructor(props){
      super(props)
      this.state = {
      }
    }

    HandleHistory(){
        document.querySelector('.history').classList.remove('hidden')
    }

    render() {
        return (
            <div className="icon">
                {this.props.name === 'Сохранённые' && (
                    <img src="saved.svg" alt="сохранённые"></img>
                )}
                {this.props.name === 'История' && (
                    <img src="history.svg" alt="история" onClick={this.HandleHistory}></img>
                )}
                {this.props.name === 'Голос' && (
                    <img src="voice.svg" alt="голос"></img>
                )}
                <p>{this.props.name}</p>
            </div>
        )
    }
}