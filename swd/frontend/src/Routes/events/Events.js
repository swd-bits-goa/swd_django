
import React from "react";

import { Mobile } from "../../Components/Responsive";
import SingleEvent from "../../Components/SingleEvent/SingleEvent";



class Events extends React.Component {

    render() {
        return (

            <Mobile>
                <SingleEvent/>
            </Mobile>

        );
    }
}


export default Events;
