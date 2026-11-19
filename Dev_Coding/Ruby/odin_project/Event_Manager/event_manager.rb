# Made by: Hazzard
# The Odin Project - Ruby: Event Manager. Reads attendees from CSV, cleans ZIP codes and phone
# numbers, finds the peak registration hours and weekdays, and writes one thank-you letter per
# attendee with ERB. Uses only the standard library (no API key).
# Run: ruby event_manager.rb   |   self-check: ruby event_manager.rb --check

require 'csv'
require 'erb'
require 'time'

DATA_FILE = File.join(__dir__, 'data', 'event_attendees.csv')
OUTPUT_DIR = File.join(__dir__, 'output')
TEMPLATE = File.join(__dir__, 'form_letter.erb')
REQUIRED_COLUMNS = %i[id regdate first_name homephone zipcode].freeze

# ==============================================================================
# Cleaning
# ==============================================================================
def clean_zipcode(zipcode)
  zipcode.to_s.rjust(5, '0')[0..4]
end

# 10 digits are fine; 11 digits starting with 1 drop the 1; anything else is invalid (nil).
def clean_phone_number(phone)
  digits = phone.to_s.gsub(/\D/, '')
  return digits if digits.length == 10
  return digits[1..] if digits.length == 11 && digits.start_with?('1')

  nil
end

def parse_registration(text)
  Time.strptime(text.to_s, '%m/%d/%y %H:%M')
rescue ArgumentError
  nil
end

# ==============================================================================
# Steps
# ==============================================================================
def read_attendees(path = DATA_FILE)
  raise "Data file not found: #{path}" unless File.exist?(path)

  rows = CSV.read(path, headers: true, header_converters: :symbol)
  missing = REQUIRED_COLUMNS - rows.headers
  raise ArgumentError, "Missing columns: #{missing.join(', ')}" unless missing.empty?

  rows
end

def peak(times, &key)
  counts = times.map(&key).tally
  top = counts.values.max
  counts.select { |_, count| count == top }.keys.sort
end

def write_letter(template, id, name, zipcode)
  Dir.mkdir(OUTPUT_DIR) unless Dir.exist?(OUTPUT_DIR)
  letter = template.result(binding)
  File.write(File.join(OUTPUT_DIR, "thanks_#{id.to_i}.html"), letter)
end

def run
  attendees = read_attendees
  template = ERB.new(File.read(TEMPLATE))
  bad_phones = []
  times = []

  attendees.each do |row|
    zipcode = clean_zipcode(row[:zipcode])
    phone = clean_phone_number(row[:homephone])
    bad_phones << row[:id] if phone.nil?
    time = parse_registration(row[:regdate])
    times << time if time
    write_letter(template, row[:id], row[:first_name], zipcode)
  end

  puts "Letters written: #{attendees.size} (in #{OUTPUT_DIR})"
  puts "Invalid phone numbers: #{bad_phones.size} (ids #{bad_phones.join(', ')})"
  puts "Unreadable registration dates: #{attendees.size - times.size}" if times.size < attendees.size
  puts "Peak hour(s): #{peak(times, &:hour).map { |h| format('%02d:00', h) }.join(', ')}"
  puts "Peak weekday(s): #{peak(times, &:wday).map { |d| Date::DAYNAMES[d] }.join(', ')}"
end

def self_check
  raise 'zip pad failed' unless clean_zipcode('501') == '00501'
  raise 'zip long failed' unless clean_zipcode('123456') == '12345'
  raise 'zip empty failed' unless clean_zipcode(nil) == '00000'
  raise 'phone 10 failed' unless clean_phone_number('(555) 010-0102') == '5550100102'
  raise 'phone 11 with 1 failed' unless clean_phone_number('15550100103') == '5550100103'
  raise 'phone 11 bad failed' unless clean_phone_number('25550100104').nil?
  raise 'phone short failed' unless clean_phone_number('555010010').nil?
  raise 'time failed' unless parse_registration('11/12/08 10:47')&.hour == 10
  raise 'peak failed' unless peak([1, 2, 2, 3, 3], &:itself) == [2, 3]
  rows = read_attendees
  raise 'row count failed' unless rows.size == 12

  puts 'Self-check passed.'
end

if __FILE__ == $PROGRAM_NAME
  ARGV.include?('--check') ? self_check : run
end
