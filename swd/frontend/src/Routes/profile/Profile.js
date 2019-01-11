/* eslint no-unused-vars:0 */

import React from "react";
import {Mobile} from "../../Components/Responsive";
import { Tablet } from '../Components/Responsive';
import s from "./Profile.css";
import {Card, CardMedia, Paper} from "material-ui";
import pic from "./DefaultPic.svg";

import gql from "graphql-tag";
import { graphql } from "react-apollo";

class Profile extends React.Component {
    render() {
        const { loading, error, currentUser } = this.props.data;
        if(loading){
            return <h4>loading..</h4>
        }
        if(error){
            return <h4>{error.message}</h4>
        } 
        console.log(this.props.data);
        return (
            <Mobile>
                <div className={s.container}>
                <h2>Profile</h2>
                    <div className={s.profileImg}>
                        <CardMedia>
                            <img src={pic} style={{width: "100%", minWidth: "20%" , box-shadow: 0px 4px 4px rgba(0, 0, 0, 0.25)}} alt="profile_pic"/>
                        </CardMedia>
                    </div>
                    <div className={s.paperDiv}>
                        <Paper zDepth={1} style={{borderRadius: 4, margin: 4, padding: 3, font-family: 'Montserrat',
  fontWeight: 'semibold'}}>

                            <div className={s.infoPaper}>
                                <div className={s.paperElement}>
                                    <div className={s.column1} style={color: '#F46036', line-height: 'normal';
font-size: '32px'; }>
                                        <p><b>Name</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>{currentUser.firstName+" "+currentUser.lastName}</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>ID</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>{currentUser.student.bitsId}</p>
                                    </div>
                                </div>
                                
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        {currentUser.student.hostelps.acadstudent?<p><b>Hostel </b></p>:<p><b>PS Station</b></p>}
                                    </div>
                                    <div className={s.column2}>
                                        {currentUser.student.hostelps.acadstudent?<p>{currentUser.student.hostelps.hostel}</p>:<p>{currentUser.student.hostelps.psStation}</p>}
                                    </div>
                                </div>
                                {currentUser.student.hostelps.acadstudent?
                                    <div className={s.paperElement}>
                                        <div className={s.column1}>
                                            <p><b>Hostel Room </b></p>
                                        </div>
                                        <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>DOB</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>{currentUser.student.bDay}</p>
                                    </div>
                                </div>
                                        <div className={s.column2}>
                                            <p>{currentUser.student.hostelps.room}</p>
                                        </div>
                                    </div>:null}
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>CGPA</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>{currentUser.student.cgpa}</p>
                                    </div>
                                </div>
                            </div>
                        </Paper>
                    </div>
                    <div className={s.paperDiv}>
                        <Paper zDepth={1} style={{borderRadius: 4, margin: 4, padding: 3}}>
                            <div className={s.infoPaper}>
                                <p><b>Permanent Address</b></p>
                                <p style={{lineHeight: 2}}>{currentUser.student.address}</p>
                            </div>
                        </Paper>
                    </div>
                    

                        </Paper>

                    </div>
                </div>
                <ButtonToolbar>
  <Button href="home.html" style={{font-family: 'Montserrat',font-style: 'normal',font-weight: 600, line-height: 'normal',font-size: 22px,
text-align: 'center',color: ' #074F57',background: '#FFBE57'}}>GO Back</Button>
  <Button style={{padding-top: '12px',padding-bottom: '12px'}}>GO Back</Button>
</ButtonToolbar>;
            </Mobile>

        );

    }
}

const GetCurrentUser = gql`
  query GetCurrentUser {
    currentUser {
      id
      username
      firstName
      lastName
      student{
        bDay
        hostelps{
            psStation
            acadstudent
            hostel
            room
        }
        bitsId
        cgpa
        address
        phone
      }
  }
}
`;


export default graphql(GetCurrentUser)(Profile);
