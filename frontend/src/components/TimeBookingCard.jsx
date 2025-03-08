
function TimeBookingCard(props) {

  const {booking} = props


  return (
    <div>
      <Card
      title={booking.name}
      style={{
        width: 300,
      }}
    >
      <p>Card content</p>
      <p>Card content</p>
      <p>Card content</p>
      </Card>
    </div>
  )
}

export default TimeBookingCard