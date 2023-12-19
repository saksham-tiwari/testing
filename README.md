# Flexmoney Assignment - Yoga Submission Form

Requirements for the admission form are:
- Only people within the age limit of 18-65 can enroll for the monthly classes and they will
be paying the fees on a month on month basis. I.e. an individual will have to pay the fees
every month and he can pay it any time of the month.
- They can enroll any day but they will have to pay for the entire month. The monthly fee is
500/- Rs INR.
- There are a total of 4 batches a day namely 6-7AM, 7-8AM, 8-9AM and 5-6PM. The
participants can choose any batch in a month and can move to any other batch next
month. I.e. participants can shift from one batch to another in different months but in the
same month they need to be in the same batch.

The above APIs can be found at `/api/v1/schema/docs/` and `/api/v1/schema/redoc/` endpoint.

## Setup
### To Create Local Setup
1. Clone the repository:

```CMD
git clone https://github.com/GeekGawd/flexmoney-assignment
```
To run the server, you need to have Python installed on your machine. If you don't have it installed, you can follow the instructions [here](https://www.geeksforgeeks.org/download-and-install-python-3-latest-version/) to install it.

2. Install & Create a virtual environment:

```CMD
pip install virtualenv
virtualenv venv
```

3. Activate the virtual environment:
```CMD
./venv/scripts/activate
```

4. Install the dependencies: 

```CMD
pip install -r requirements.txt
```

5. To Check if it is working correctly run tests
```CMD
python manage.py test
```
<!-- 
### Docker Setup

```CMD
docker-compose up --build -d
``` -->

## Database Design

I used uuid field in all the models to create a external id and used the internal Autoincrement ID in all the tables as primary key. 

I did this because of security and performance reasons, managing uuid as primary key is very cumbersome and can lead to loss in read performance. However, Autoincrement field can lead to security issues.

So, I used both as the best of the worlds


![Database ERD](https://i.imgur.com/WqUyg93.png)


### Yoga Booking
This model represents a booking made by a user for a yoga class. It includes fields for the user’s name, email, and date of birth, and a created_at field that records when the booking was made. It also has a foreign key to the YogaBatch model.

### Yoga Batch
This model represents a batch of yoga classes for a specific month of a specific year. It includes fields for the year and month, and a created_at field that records when the batch was created.

There could be only on yoga batch created each month of each year. Each Batch would have yoga timings available for slot booking.

### Yoga Timing
This model represents the timings for the yoga classes. It includes fields for the start and end times of a class, and a timespan field that combines these two. It also has a foreign key to the YogaBatch model.

To make this scalable so the yoga business can include more timings in the future I created a yoga timing model which is associated with the yoga batch using one to many relationship.

I have also included a timespan field to easily check for overlapping batch timings and do range query in database.

### Offer
This model represents an offer that can be applied to a booking. It includes fields for the name of the offer, the discount it provides, the number of times it can be used, and a unique code for the offer.

### Order

This model represents an order made by a user. It includes fields for the amount and currency of the order, the status of the order (created, paid, or cancelled), and a created_at field that records when the order was made. It also has foreign keys to the YogaBooking, YogaBatch, YogaTimings, and Offer models.

This is used to do the transaction and create a corresponding order for the user.

### Email Service

Implemented sending email to the user with order id so they can verify their purchase at the yoga center.

### Future Scope

- Could have dockerised the application as well not much issue here, but have an exam tomorrow, so because of the time crunch skiping it.

## Notable Libraries Used

- python-decouple - For environment variable
- drf-spectacular - To generate seagger documentation.