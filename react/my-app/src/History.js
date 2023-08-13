import { Component } from "react";
export default class History extends Component {
    constructor(props){
      super(props)
      this.state = {
      }
    }

    render() {
        return (
            <div className="history hidden">
                <p>История</p>
                {
                    this.props.History.map((item) => 
                        <div className="element">{item}</div>
                    )
                }
            </div>
        )
    }
}