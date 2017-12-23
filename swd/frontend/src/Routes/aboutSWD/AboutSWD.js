/* eslint no-unused-vars:0 */

import React from "react";
import PropTypes from "prop-types";
import { Mobile } from "../../Components/Responsive";
import ExpandableCard from "../../Components/ExpandableCard";
import s from "./AboutSWD.css";
import gql from "graphql-tag";
import { graphql } from "react-apollo";



class AboutSWD extends React.Component {

  // const data = (props) => {
  //   const loading = props.data.loading;
  //   const error = props.data.error;
  //   const currentUser = props.data.currentUser;
  //   // render UI with loading, error, or currentUser
  // }

  render() {
    return (
        
      <Mobile>
        <div className={s.container}>
          <ExpandableCard title="Hostel Facilities" text="sfsf"/>
          <ExpandableCard title="Mess Facilities" text="sfsf"/>
          <ExpandableCard title = "Financial Aid" text = "sfsf" />
          <ExpandableCard title = "Online Services" text = "sfsf" />
          </div>
      </Mobile>
      
    );
  }
}


export default AboutSWD;
